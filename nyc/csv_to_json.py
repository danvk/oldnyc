#!/usr/bin/env python
#
# Converts the milstein.csv file to a JSON file.

import csv
import json
from record import Record


def convert_csv_row(row: dict) -> Record:
    url = row["IMAGE_Permalink"].strip()
    assert url

    img_url = row["IMG_URL"].strip()
    assert img_url

    photo_id = row["DIGITAL_ID"].strip()
    assert photo_id

    date_str = row["CREATED_DATE"].strip()
    # date_str is not always present

    full_address = row["Full Address"].strip()

    title = row["IMAGE_TITLE"].strip()
    assert title

    alt_title = row["ALTERNATE_TITLE"].strip()

    r: Record = {
        "id": photo_id,
        "photo_url": img_url,
        "preferred_url": url,
        "location": full_address,
        "date": date_str,
        "title": title,
        "alt_title": alt_title,
    }
    return r


if __name__ == "__main__":
    output_file = "nyc/records.json"

    records = []
    for row in csv.DictReader(open("nyc/milstein.csv", encoding="latin-1")):
        r = convert_csv_row(row)
        records.append(r)

    with open(output_file, "w") as out:
        json.dump(records, out)

    print("Wrote %d records" % len(records))
