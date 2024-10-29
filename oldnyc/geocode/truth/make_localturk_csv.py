#!/usr/bin/env python
import csv
import dataclasses
import json
import sys

from oldnyc.item import load_items


def make_csv(ids_file: str, id_to_location: dict, csv_file: str):
    items = load_items("data/images.ndjson")
    id_to_item = {r.id: r for r in items}
    ids = open(ids_file).read().splitlines()

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
        print(
            "Usage: python json_to_csv.py <ids_file> <input id-to-location.json> <output_csv_file>"
        )
        sys.exit(1)

    ids_file = sys.argv[1]
    id_to_location = json.load(open(sys.argv[2]))
    csv_file = sys.argv[3]
    make_csv(ids_file, id_to_location, csv_file)
