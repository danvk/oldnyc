#!/usr/bin/env python


import base64
import csv
import fileinput
import json


def main():
    rows = csv.DictReader(fileinput.input())
    # back_id,BASE64,Before,notes,Neutral,After
    for row in rows:
        back_id = row["back_id"]
        record = json.loads(base64.b64decode(row["BASE64"]).decode("utf-8"))
        before = row["Before"]
        notes = row["notes"]
        # neutral = row["Neutral"]
        after = row["After"]
        result = "Site" if before else "GPT" if after else "Neutral"
        d = record["metadata"]["distance"]
        print(f"{back_id}\t{result}\t{d}\t{notes}")


if __name__ == "__main__":
    main()
