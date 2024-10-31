#!/usr/bin/env python
"""Convert images to CSV for manual geocoding with the localturk template.

This also takes in a GeoJSON file with provisional geocodes, to be confirmed.
"""

import csv
import json
import sys

import pygeojson


def assert_point(g: pygeojson.GeometryObject) -> pygeojson.Point:
    if not isinstance(g, pygeojson.Point):
        raise ValueError(f"Expected Point, got {g}")
    return g


def geojson_to_csv(ndjson_file: str, geojson_file: str, out_csv_file: str):
    features = pygeojson.load_feature_collection(open(geojson_file)).features
    id_to_location = {
        f.properties["id"]: assert_point(f.geometry).coordinates if f.geometry else None
        for f in features
    }
    with open(ndjson_file, "r") as ndjson_f, open(out_csv_file, "w", newline="") as csv_f:
        writer = None
        for line in ndjson_f:
            record = json.loads(line)
            record["location"] = id_to_location.get(record["id"]) or "null"
            if writer is None:
                writer = csv.DictWriter(csv_f, fieldnames=record.keys())
                writer.writeheader()
            writer.writerow(record)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python geojson_to_csv.py <images.ndjson> <images.geojson> <output_csv_file>")
        sys.exit(1)

    ndjson_file, geojson_file, csv_file = sys.argv[1:]
    geojson_to_csv(ndjson_file, geojson_file, csv_file)
