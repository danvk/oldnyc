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
from oldnyc.geocode.coders import extended_grid, gpt, milstein, nyc_parks
from oldnyc.geocode.geocode_types import Coder, Locatable, Location
from oldnyc.item import Item, load_items

CODERS: dict[str, Callable[[], Coder]] = {
    "extended-grid": extended_grid.ExtendedGridCoder,
    "milstein": milstein.MilsteinCoder,
    "nyc-parks": nyc_parks.NycParkCoder,
    "gpt": gpt.GptCoder,
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
        default="extended-grid,milstein,nyc-parks",
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
        "-o",
        "--output_format",
        default="",
        choices=(
            "lat-lons.js",
            "lat-lons-ny.js",
            "records.json",
            "id-location.txt",
            "id-location.json",
            "entries.txt",
            "locations.txt",
            "geojson",
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
        g = geocoder.Geocoder(args.use_network, 2)  # 2s between geocodes
        if args.use_network and not api_key:
            raise ValueError("Must set GOOGLE_MAPS_API_KEY with --use_network")
    else:
        g = None

    geocoders = [CODERS[coder_name]() for coder_name in args.coders.split(",")]
    for geocoder in geocoders:
        CODERS[geocoder.name()]  # keep the dict in sync with the name() methods

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
    located_recs: list[tuple[Item, str | None, Locatable | Location | None]] = []
    for idx, r in enumerate(rs):
        if idx % 100 == 0 and idx > 0:
            sys.stderr.write("%5d / %5d records processed\n" % (1 + idx, len(rs)))

        located_rec = (r, None, None)

        # Give each coder a crack at the record, in turn.
        for c in geocoders:
            location_data = c.codeRecord(r)
            if not location_data:
                continue
            assert "address" in location_data

            if not g:
                if args.print_records:
                    print("%s\t%s\t%s" % (c.name(), r.id, json.dumps(location_data)))
                stats[c.name()] += 1
                located_rec = (r, c.name(), location_data)
                break

            lat_lon = None
            try:
                geocode_result = None
                address = location_data["address"]
                try:
                    geocode_result = g.Locate(address)
                except urllib.error.HTTPError as e:
                    if e.status == 400:
                        sys.stderr.write(f"Bad request: {address}\n")
                    else:
                        raise e

                if geocode_result:
                    lat_lon = c.getLatLonFromGeocode(geocode_result, location_data, r)
                else:
                    sys.stderr.write("Failed to geocode %s\n" % r.id)
                    # sys.stderr.write('Location: %s\n' % location_data['address'])
            except Exception:
                sys.stderr.write("ERROR locating %s with %s\n" % (r.id, c.name()))
                # sys.stderr.write('ERROR location: "%s"\n' % json.dumps(location_data))
                raise

            if lat_lon:
                location_data["lat"] = lat_lon[0]
                location_data["lon"] = lat_lon[1]
                if args.print_records:
                    print(
                        "%s\t%f,%f\t%s\t%s"
                        % (
                            r.id,
                            lat_lon[0],
                            lat_lon[1],
                            c.name(),
                            json.dumps(location_data),
                        )
                    )
                stats[c.name()] += 1
                located_rec = (r, c.name(), location_data)
                break

        located_recs.append(located_rec)

    # Let each geocoder know we're done. This is useful for printing debug info.
    for c in geocoders:
        c.finalize()

    successes = 0
    for c in geocoders:
        sys.stderr.write("%5d %s\n" % (stats[c.name()], c.name()))
        successes += stats[c.name()]

    sys.stderr.write("%5d (total)\n" % successes)

    # TODO: are all these necessary?
    if args.output_format == "lat-lons.js":
        generate_js.printJson(located_recs, lat_lon_map)
    if args.output_format == "lat-lons-ny.js":
        generate_js.printJsonNoYears(located_recs, lat_lon_map)
    elif args.output_format == "records.json":
        generate_js.printRecordsJson(located_recs)
    elif args.output_format == "id-location.txt":
        generate_js.printIdLocation(located_recs)
    elif args.output_format == "id-location.json":
        generate_js.printLocationsJson(located_recs)
    elif args.output_format == "entries.txt":
        generate_js.printRecordsText(located_recs)
    elif args.output_format == "locations.txt":
        generate_js.printLocations(located_recs)
    elif args.output_format == "geojson":
        generate_js.output_geojson(located_recs, rs)
    else:
        raise ValueError(args.output_format)
