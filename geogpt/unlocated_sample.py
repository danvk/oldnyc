#!/usr/bin/env python
"""Print out a sample of photo IDs without location information."""

import sys
import json
import random

from record import Record


if __name__ == "__main__":
    n = int(sys.argv[1])
    site_photos = json.load(open("../oldnyc.github.io/data.json"))["photos"]
    located_ids = {photo["photo_id"].split("-")[0] for photo in site_photos}
    all_records: list[Record] = json.load(open("nyc/records.json"))
    unlocated_ids = [
        r["id"]
        for r in all_records
        if r["id"] not in located_ids and not r["outside_nyc"]
    ]
    random.shuffle(unlocated_ids)
    sys.stderr.write(f"Sampling {n} / {len(unlocated_ids)} records.\n")
    for id in unlocated_ids[:n]:
        print(id)
