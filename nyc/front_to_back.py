#!/usr/bin/env python
"""Given a list of front image IDs, output a list of back image IDs.

Outputs blank lines if the image doesn't have an associated back ID.
"""

import json
import fileinput

from record import Record


if __name__ == "__main__":
    records: list[Record] = json.load(open("nyc/records.json"))
    id_to_record = {r["id"]: r for r in records}

    for line in fileinput.input():
        front_id = line.strip()
        print(id_to_record[front_id]["back_id"] or "")
