#!/usr/bin/env python
import csv
import json
import sys


def ndjson_to_csv(ndjson_file, id_to_location: dict, csv_file):
    with open(ndjson_file, "r") as ndjson_f, open(csv_file, "w", newline="") as csv_f:
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
        print(
            "Usage: python json_to_csv.py <input_ndjson_file> <input id-to-location.json> <output_csv_file>"
        )
        sys.exit(1)

    ndjson_file = sys.argv[1]
    id_to_location = json.load(open(sys.argv[2]))
    csv_file = sys.argv[3]
    ndjson_to_csv(ndjson_file, id_to_location, csv_file)
