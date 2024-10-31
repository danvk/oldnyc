#!/usr/bin/env python
import csv
import dataclasses
import sys

import pygeojson

from oldnyc.item import load_items


def assert_point(g: pygeojson.GeometryObject) -> pygeojson.Point:
    if not isinstance(g, pygeojson.Point):
        raise ValueError(f"Expected Point, got {g}")
    return g


def make_csv(ids_file: str, geojson_file: str, csv_file: str):
    items = load_items("data/images.ndjson")
    id_to_item = {r.id: r for r in items}
    ids = open(ids_file).read().splitlines()

    features = pygeojson.load_feature_collection(open(geojson_file)).features
    id_to_location = {
        # TODO: Round
        f.id: [round(x, 6) for x in assert_point(f.geometry).coordinates][::-1]
        if f.geometry
        else None
        for f in features
    }

    with open(csv_file, "w", newline="") as csv_f:
        writer = None
        for id in ids:
            r = id_to_item.get(id)
            if not r:
                continue
            record = dataclasses.asdict(r)
            record["location"] = id_to_location.get(r.id) or "null"
            if writer is None:
                writer = csv.DictWriter(csv_f, fieldnames=record.keys())
                writer.writeheader()
            writer.writerow(record)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python json_to_csv.py <ids_file> <images.geojson> <output_csv_file>")
        sys.exit(1)

    ids_file, geojson_file, csv_file = sys.argv[1:]
    make_csv(ids_file, geojson_file, csv_file)
