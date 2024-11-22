#!/usr/bin/env python
#
# This is the main driver for the geocoding process.
# Inputs are images.ndjson and a collection of 'coders'.
# Output depends on flags, but can be JSON, GeoJSON, JavaScript, text, etc.

import argparse
import json
import os
import sys
import urllib.error
from collections import defaultdict
from typing import Callable

from dotenv import load_dotenv

from oldnyc.geocode import generate_js, geocoder
from oldnyc.geocode.coders import (
    gpt,
    special_cases,
    subjects,
    title_pattern,
)
from oldnyc.geocode.geocode_types import Coder, Locatable
from oldnyc.geocode.locatable import (
    Point,
    extract_point_from_google_geocode,
    get_address_for_google,
    locate_with_osm,
)
from oldnyc.geocode.locatable import (
    counts as locatable_counts,
)
from oldnyc.item import Item, load_items

CODERS: dict[str, Callable[[], Coder]] = {
    "title-cross": title_pattern.TitleCrossCoder,
    "title-address": title_pattern.TitleAddressCoder,
    "subjects": subjects.SubjectsCoder,
    "gpt": gpt.GptCoder,
    "special": special_cases.SpecialCasesCoder,
}

if __name__ == "__main__":
    load_dotenv()
    parser = argparse.ArgumentParser(description="Generate geocodes")
    parser.add_argument(
        "--images_ndjson",
        required=True,
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
        default="title-cross,title-address,gpt,special,subjects",
        help="Set to a comma-separated list of coders. Coders run in the specified order.",
    )

    parser.add_argument(
        "-g",
        "--geocode",
        action="store_true",
        help="Set to geocode all locations. The alternative is "
        "to extract location strings but not geocode them. This "
        "can be useful with --print_records.",
    )
    parser.add_argument(
        "-n",
        "--use_network",
        action="store_true",
        help="Set this to make the geocoder use the network. The "
        "alternative is to use only the geocache.",
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

    args = parser.parse_args()

    if args.geocode:
        api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
        g = geocoder.Geocoder(args.use_network, 2, api_key)  # 2s between geocodes
        if args.use_network and not api_key:
            raise ValueError("Must set GOOGLE_MAPS_API_KEY with --use_network")
    else:
        g = None

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

    stats = defaultdict(int)
    located_recs: list[tuple[Item, tuple[str, Locatable, Point] | None]] = []
    for idx, r in enumerate(rs):
        if idx % 100 == 0 and idx > 0:
            sys.stderr.write("%5d / %5d records processed\n" % (1 + idx, len(rs)))

        located_rec = (r, None)

        # Give each coder a crack at the record, in turn.
        for c in geocoders:
            locatable = c.code_record(r)
            if not locatable:
                continue

            if not g:
                if args.print_records:
                    print("%s\t%s\t%s" % (c.name(), r.id, json.dumps(locatable)))
                stats[c.name()] += 1
                located_rec = (r, None)
                break

            # First try OSM (offline), then Google (online)
            lat_lon = locate_with_osm(r, locatable, c.name())

            if not lat_lon:
                try:
                    geocode_result = None
                    address = get_address_for_google(locatable)
                    try:
                        if args.print_geocodes:
                            geocache = geocoder.cache_file_name(address)
                            print(f'{r.id} {c.name()}: Geocoding "{address}" ({geocache})')
                        geocode_result = g.Locate(address, True, r.id)
                    except urllib.error.HTTPError as e:
                        if e.status == 400:
                            sys.stderr.write(f"Bad request: {address}\n")
                        else:
                            raise e

                    if geocode_result:
                        lat_lon = extract_point_from_google_geocode(
                            geocode_result, locatable, r, c.name()
                        )
                    else:
                        sys.stderr.write("Failed to geocode %s\n" % r.id)
                        # sys.stderr.write('Location: %s\n' % location_data['address'])
                except Exception:
                    sys.stderr.write("ERROR locating %s with %s\n" % (r.id, c.name()))
                    # sys.stderr.write('ERROR location: "%s"\n' % json.dumps(location_data))
                    raise

            if lat_lon:
                if args.print_records:
                    print(
                        "%s\t%f,%f\t%s\t%s"
                        % (
                            r.id,
                            lat_lon[0],
                            lat_lon[1],
                            c.name(),
                            json.dumps(locatable),
                        )
                    )
                stats[c.name()] += 1
                located_rec = (r, (c.name(), locatable, lat_lon))
                break

        located_recs.append(located_rec)

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
        if n_google_attempts:
            sys.stderr.write(f"          google: {n_google_success}\n")
            sys.stderr.write(f"   boro mismatch: {n_boro_mismatch}\n")
            sys.stderr.write(f"        failures: {n_google_fail}\n")

    # grid.log_stats()

    sys.stderr.write("-- Final stats --\n")
    successes = 0
    for c in geocoders:
        sys.stderr.write("%5d %s\n" % (stats[c.name()], c.name()))
        successes += stats[c.name()]

    sys.stderr.write("%5d (total)\n" % successes)

    if args.output_format == "lat-lon-to-ids.json":
        generate_js.printJsonNoYears(located_recs, lat_lon_map)
    elif args.output_format == "id-location.txt":
        generate_js.printIdLocation(located_recs)
    elif args.output_format == "geojson":
        generate_js.output_geojson(located_recs, rs)
    elif args.output_format == "none":
        pass
    else:
        raise ValueError(args.output_format)

    if args.cache_hits_file:
        assert g
        with open(args.cache_hits_file, "w") as out:
            out.write("\n".join(g._touched_cache_files))
            out.write("\n")
