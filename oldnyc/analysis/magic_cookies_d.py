#!/usr/bin/env python

import csv
import fileinput

from oldnyc.util import decode_json_base64


def main():
    rows = csv.DictReader(fileinput.input())
    # back_id,BASE64,Before,notes,Neutral,After
    for row in rows:
        back_id = row["back_id"]
        record = decode_json_base64(row["BASE64"])
        before = row["Before"]
        notes = row["notes"]
        # neutral = row["Neutral"]
        after = row["After"]
        result = "Site" if before else "GPT" if after else "Neutral"
        d = record["metadata"]["distance"]
        print(f"{back_id}\t{result}\t{d}\t{notes}")


if __name__ == "__main__":
    main()
