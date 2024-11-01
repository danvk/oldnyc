#!/usr/bin/env python
"""Assemble un-located subjects into a CSV file for localturking."""

import base64
import csv
import dataclasses
import json
import os
from collections import Counter, defaultdict

from oldnyc.geocode.coders.nyc_parks import IGNORE_SUBJECTS, NycParkCoder
from oldnyc.item import Item, load_items


def main():
    items = load_items("data/images.ndjson")
    coder = NycParkCoder()

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

    assert not os.path.exists("data/subjects/out.csv")

    # TODO: read existing out.csv
    with (
        open("data/subjects/tasks.csv", "w") as tasks_f,
        open("data/subjects/out.csv", "w") as out_f,
    ):
        tasks = csv.DictWriter(tasks_f, fieldnames=["geo", "count", "examples_json_b64"])
        tasks.writeheader()
        out = csv.DictWriter(
            out_f, fieldnames=["geo", "count", "examples_json_b64", "outcome", "latlng"]
        )
        out.writeheader()

        for geo, count in counts.most_common():
            examples = [dataclasses.asdict(item) for item in geo_to_items[geo][:5]]
            lat_lng = locations.get(geo)
            examples_json_b64 = base64.b64encode(json.dumps(examples).encode("utf8")).decode("utf8")
            tasks.writerow(
                {
                    "geo": geo,
                    "count": count,
                    "examples_json_b64": examples_json_b64,
                }
            )
            if lat_lng:
                out.writerow(
                    {
                        "geo": geo,
                        "count": count,
                        "examples_json_b64": examples_json_b64,
                        "outcome": "nyc_parks",
                        "latlng": lat_lng,
                    }
                )


if __name__ == "__main__":
    main()
