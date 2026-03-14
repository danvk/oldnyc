#!/usr/bin/env python
#
# This is the main driver for the geocoding process.
# Inputs are images.ndjson and a collection of 'coders'.
# Output depends on flags, but can be JSON, GeoJSON, JavaScript, text, etc.

import argparse
import json
import logging
import os
import sys
from collections import defaultdict
from dataclasses import asdict
from typing import Callable

from dotenv import load_dotenv
from tqdm import tqdm

from oldnyc.geocode import generate_js, geocoder, grid
from oldnyc.geocode.coders import (
    gpt,
    special_cases,
    subjects,
    title_pattern,
)
from oldnyc.geocode.geocode_types import (
    AddressLocation,
    Coder,
    GeocodedItem,
    GeocodeResult,
)
from oldnyc.geocode.locatable import (
    counts as locatable_counts,
)
from oldnyc.geocode.locatable import (
    locate_with_google,
    locate_with_osm,
    total_counts,
)
from oldnyc.item import load_items

CODERS: dict[str, Callable[[], Coder]] = {
    "title-cross": title_pattern.TitleCrossCoder,
    "title-address": title_pattern.TitleAddressCoder,
    "subjects": subjects.SubjectsCoder,
    "gpt": gpt.GptCoder,
    "special": special_cases.SpecialCasesCoder,
    "fifth": special_cases.FifthAvenueCoder,
}


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Generate geocodes")
    parser.add_argument(
        "--images_ndjson",
        default="data/images.ndjson",
        help="ndjson file containing images (usually images.ndjson or photos.ndjson)",
    )
    parser.add_argument(
        "--ids_filter",
        default="",
        help="Comma-separated list of Photo IDs to consider, or path to an IDs file",
    )
    parser.add_argument(
        "-c",
        "--coders",
        default="fifth,title-cross,title-address,gpt,special,subjects",
        help="Set to a comma-separated list of coders. Coders run in the specified order.",
    )

    parser.add_argument(
        "-n",
        "--use_network",
        action="store_true",
        help="Set this to make the geocoder use the network. The "
        "alternative is to use only the geocache.",
    )
    parser.add_argument(
        "--google",
        default="all",
        choices=("all", "none", "address-only"),
        help="How to use Google for geocoding. all=intersections + addresses. "
        "none results in OSM-only geocoding.",
    )

    parser.add_argument(
        "-p",
        "--print_records",
        action="store_true",
        help="Set to print out records as they're coded.",
    )
    parser.add_argument(
        "--print_geocodes",
        action="store_true",
        help="Print Google Maps geocoding queries as they're performed.",
    )
    parser.add_argument(
        "--cache_hits_file",
        type=str,
        help="Write a list of geocache hits to this file; can be fed to purge_geocache.py.",
    )
    parser.add_argument(
        "-o",
        "--output_format",
        default="",
        choices=(
            "lat-lon-to-ids.json",  # used for the static site; TODO: replace with geojson
            "id-location.txt",  # used in the e2e test
            "geojson",
            "none",  # i.e. if you only want stats
        ),
    )
    parser.add_argument(
        "--lat_lon_map",
        default="",
        help="Lat/lon cluster map, built by cluster-locations.py. "
        "Only used when outputting lat-lons{,-ny}.js",
    )
    parser.add_argument("--no-progress-bar", action="store_true", help="Show/hide progress bar.")
    parser.add_argument(
        "--debug",
        metavar="MODULE",
        nargs="+",
        default=[],
        help="Enable DEBUG logging for the specified module(s), e.g. oldnyc.geocode.coders.gpt",
    )

    args = parser.parse_args()

    logger = logging.getLogger("oldnyc.geocode")
    logging.basicConfig(level=logging.WARNING, format="%(name)s %(levelname)s %(message)s")
    for module in args.debug:
        logging.getLogger(module).setLevel(logging.DEBUG)

    api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    g = (
        geocoder.Geocoder(args.use_network, 2, api_key) if args.google != "none" else None
    )  # 2s between geocodes
    if args.use_network and not api_key:
        raise ValueError("Must set GOOGLE_MAPS_API_KEY with --use_network")

    geocoders = [CODERS[coder_name]() for coder_name in args.coders.split(",")]
    for coder in geocoders:
        CODERS[coder.name()]  # keep the dict in sync with the name() methods

    # TODO(danvk): does this belong here?
    lat_lon_map: dict[str, str] = {}
    if args.lat_lon_map:
        for line in open(args.lat_lon_map):
            line = line.strip()
            if not line:
                continue
            old, new = line.split("->")
            lat_lon_map[old] = new

    rs = load_items(args.images_ndjson)
    if args.ids_filter:
        n_before = len(rs)
        ids_filter = args.ids_filter
        if "," not in ids_filter and (os.path.exists(ids_filter) or "/" in ids_filter):
            ids = set(open(ids_filter).read().strip().split("\n"))
        else:
            ids = set(ids_filter.split(","))
        rs = [r for r in rs if r.id in ids]
        n_after = len(rs)
        sys.stderr.write(
            f"Filtered to {n_after}/{n_before} records with --ids_filter ({len(ids)})\n"
        )

    grid_geocoder = grid.Grid()

    stats = defaultdict(int)
    geocoded_items: list[GeocodedItem] = []
    src = rs if args.no_progress_bar else tqdm(rs)
    for r in src:
        result = GeocodedItem(item=r, result=None, failures=[])

        # Give each coder a crack at the record, in turn.
        for c in geocoders:
            candidate_locatables = c.code_record(r)
            if not candidate_locatables:
                continue

            lat_lon = None
            locatable = None
            for locatable in candidate_locatables:
                # First try OSM (offline), then Google (online)
                lat_lon = locate_with_osm(r, locatable, c.name(), grid_geocoder)
                logger.debug(f"{r.id}: {c.name()} {json.dumps(asdict(locatable))} OSM: {lat_lon}")
                geocode_provider = "osm"

                if not lat_lon and g:
                    if args.google != "address" or isinstance(locatable, AddressLocation):
                        lat_lon = locate_with_google(locatable, r, c.name(), g, args.print_geocodes)
                        logger.debug(
                            f"{r.id}: {c.name()} {json.dumps(asdict(locatable))} Google: {lat_lon}"
                        )
                        geocode_provider = "google"

                if lat_lon:
                    if args.print_records:
                        print(
                            "%s\t%f,%f\t%s\t%s"
                            % (
                                r.id,
                                lat_lon[0],
                                lat_lon[1],
                                c.name(),
                                json.dumps(asdict(locatable)),
                            )
                        )
                    stats[c.name()] += 1
                    result.result = GeocodeResult(
                        coder=c.name(),
                        location=locatable,
                        lat_lon=lat_lon,
                        geocoder=geocode_provider,
                    )
                    break
                result.failures.append((c.name(), locatable))

            if lat_lon:
                break

        geocoded_items.append(result)

    # Let each geocoder know we're done. This is useful for printing debug info.
    for c in geocoders:
        sys.stderr.write(f"-- Finalizing {c.name()} --\n")
        c.finalize()
        counts = locatable_counts[c.name()]
        n_grid_attempt = counts["grid: attempt"]
        n_grid = counts["grid: success"]
        n_boro_mismatch = counts["google: boro mismatch"]
        n_google_fail = counts["google: fail"]
        n_google_success = counts["google: success"]
        n_google_attempts = n_google_fail + n_google_success + n_boro_mismatch

        if n_grid_attempt:
            sys.stderr.write(f"            grid: {n_grid} ({n_grid_attempt} attempts)\n")
            grid_geocoder.log_stats()

        if n_google_attempts:
            sys.stderr.write(f"          google: {n_google_success}\n")
            sys.stderr.write(f"   boro mismatch: {n_boro_mismatch}\n")
            sys.stderr.write(f"        failures: {n_google_fail}\n")
            assert g
            g.log_stats()
            sys.stderr.write(f"{total_counts.most_common()}\n")

    sys.stderr.write("-- Final stats --\n")
    successes = 0
    for c in geocoders:
        sys.stderr.write("%5d %s\n" % (stats[c.name()], c.name()))
        successes += stats[c.name()]

    # sys.stderr.write("%s\n" % json.dumps(locatable_counts))

    sys.stderr.write("%5d (total)\n" % successes)

    if args.output_format == "id-location.txt":
        generate_js.printIdLocation(geocoded_items)
    elif args.output_format == "geojson":
        generate_js.output_geojson(geocoded_items, rs, lat_lon_map)
    elif args.output_format == "none":
        pass
    else:
        raise ValueError(args.output_format)

    if args.cache_hits_file:
        assert g
        with open(args.cache_hits_file, "w") as out:
            out.write("\n".join(g._touched_cache_files))
            out.write("\n")


if __name__ == "__main__":
    main()
