#!/usr/bin/env python
"""Assemble un-located subjects into a CSV file for localturking."""

import csv
import json
import os
import sys
from collections import Counter, defaultdict
from typing import Sequence

import pygeojson
from haversine import haversine

from oldnyc.geocode.coders.nyc_parks import IGNORE_SUBJECTS, NycParkCoder
from oldnyc.geojson_utils import assert_point
from oldnyc.item import Item, load_items
from oldnyc.util import encode_json_base64, pick


def centroid(points: Sequence[tuple[float, float]]) -> tuple[float, float]:
    x = sum(p[0] for p in points) / len(points)
    y = sum(p[1] for p in points) / len(points)
    return (x, y)


def centroid_and_extent(points: Sequence[tuple[float, float]]) -> tuple[tuple[float, float], float]:
    x, y = centroid(points)
    extent_km = max(haversine(p[::-1], (y, x)) for p in points)
    return ((x, y), 1000.0 * extent_km)


def maybe_coords(p: pygeojson.Point | None):
    return p.coordinates[:2] if p else None


def main():
    items = load_items("data/images.ndjson")
    coder = NycParkCoder()

    other_geocodes = pygeojson.load_feature_collection(open("/tmp/images.geojson")).features
    id_to_location = {str(f.id): assert_point(f.geometry) for f in other_geocodes if f.geometry}

    counts = Counter[str]()
    locations = dict[str, str]()
    geo_to_items = defaultdict[str, list[Item]](list)

    # TODO: pull in locations from other coders here.
    for item in items:
        location = coder.codeRecord(item)
        if location:
            locations[location["source"]] = location["address"][1:]
        for geo in item.subject.geographic:
            if geo in IGNORE_SUBJECTS:
                continue
            counts[geo] += 1
            geo_to_items[geo].append(item)

    csv.field_size_limit(sys.maxsize)
    existing = {}
    if os.path.exists("data/subjects/out.csv"):
        rows = csv.DictReader(open("data/subjects/out.csv"))
        # 'result' is manual review; 'outcome' is automatic from nyc_parks
        existing = {
            r["geo"]: pick(r, ("result", "latlng", "user_notes")) for r in rows if r["result"]
        }
        sys.stderr.write(f"Loaded {len(existing)} existing rows\n")

    with (
        open("data/subjects/tasks.csv", "w", newline="\n") as tasks_f,
        open("data/subjects/out.csv", "w", newline="\n") as out_f,
    ):
        fieldnames = ["geo", "count", "examples_json_b64", "centroid"]
        tasks = csv.DictWriter(tasks_f, fieldnames=fieldnames)
        tasks.writeheader()
        out = csv.DictWriter(
            out_f, fieldnames=fieldnames + ["outcome", "latlng", "result", "user_notes"]
        )
        out.writeheader()

        for geo, count in counts.most_common():
            examples = [
                {
                    "id": item.id,
                    "url": item.url,
                    "title": item.title,
                    "geocode": maybe_coords(id_to_location.get(item.id)),
                }
                for item in geo_to_items[geo]
            ]
            points = [
                p.coordinates[:2]
                for item in geo_to_items[geo]
                if (p := id_to_location.get(item.id))
            ]
            centroid_extent_m = centroid_and_extent(points) if points else None
            lat_lng = locations.get(geo)
            row = {
                "geo": geo,
                "count": count,
                "examples_json_b64": encode_json_base64(examples),
                "centroid": json.dumps(centroid_extent_m),
            }
            tasks.writerow(row)
            if lat_lng:
                out.writerow(
                    {
                        **row,
                        "outcome": "nyc_parks",
                        "latlng": lat_lng,
                    }
                )
            elif geo in existing:
                out.writerow({**row, **existing[geo]})


if __name__ == "__main__":
    main()
