#!/usr/bin/env python
"""Converts the milstein.csv file to a JSON file.

Because this is a convenient place to do it, this also adds associated
backing IDs.
"""

import csv
import re
import json
import sys
from record import Record


BOROUGHS = ("Manhattan", "Queens", "Brooklyn", "Bronx", "Staten Island")
STATES = [
    "Alabama",
    "Alaska",
    "Arizona",
    "Arkansas",
    "California",
    "Colorado",
    "Connecticut",
    "Delaware",
    "District of Columbia",
    "Florida",
    "Georgia",
    "Hawaii",
    "Idaho",
    "Illinois",
    "Indiana",
    "Iowa",
    "Kansas",
    "Kentucky",
    "Louisiana",
    "Maine",
    "Maryland",
    "Massachusetts",
    "Michigan",
    "Minnesota",
    "Mississippi",
    "Missouri",
    "Montana",
    "Nebraska",
    "Nevada",
    "New Hampshire",
    "New Jersey",
    "New Mexico",
    "New York",
    "North Carolina",
    "North Dakota",
    "Ohio",
    "Oklahoma",
    "Oregon",
    "Pennsylvania",
    "Rhode Island",
    "South Carolina",
    "South Dakota",
    "Tennessee",
    "Texas",
    "Utah",
    "Vermont",
    "Virginia",
    "Washington",
    "West Virginia",
    "Wisconsin",
    "Wyoming",
]


def extract_borough(source: str) -> str | None:
    for borough in BOROUGHS:
        if borough in source:
            return borough
    return None


def extract_state(source: str) -> str | None:
    for state in STATES:
        if state in source:
            return state
    return None


def convert_csv_row(row: dict) -> Record:
    # TODO: change this to a UUID-based URL
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

    source = row["SOURCE"].strip()
    borough = extract_borough(source)
    state = extract_state(source)
    outside_nyc = (
        state is not None and state != "New York"
    ) or "The New-York City directory" in source

    r: Record = {
        "id": photo_id,
        "photo_url": img_url,
        "preferred_url": url,
        "location": full_address,
        "date": date_str,
        "title": title,
        "alt_title": alt_title,
        "back_id": None,
        "borough": borough,
        "outside_nyc": outside_nyc,
    }
    return r


def photo_id_to_backing_id(photo_id: str) -> str:
    if "f" in photo_id:
        return re.sub(r"f?(?:-[a-z])?$", "b", photo_id, count=1)
    elif re.match(r"\d+$", photo_id):
        front = int(photo_id)
        back = front + 1
        return str(back)
    return None


def add_backing_ids(records: list[Record]):
    all_photo_ids = {r["id"] for r in records}
    for r in records:
        back_id = None
        photo_id = r["id"].split("-")[0]
        if "f" in photo_id:
            back_id = photo_id_to_backing_id(photo_id)
        elif re.match(r"\d+$", photo_id):
            possible_back_id = photo_id_to_backing_id(photo_id)
            if possible_back_id not in all_photo_ids:
                back_id = possible_back_id
        else:
            sys.stderr.write(f"Weird ID: {photo_id}\n")
        r["back_id"] = back_id
    num_back_ids = sum(1 for r in records if r["back_id"] is not None)
    sys.stderr.write(
        f"Associated back IDs with {num_back_ids}/{len(records)} photos.\n"
    )


if __name__ == "__main__":
    output_file = "nyc/records.json"

    records = []
    for row in csv.DictReader(open("nyc/milstein.csv", encoding="latin-1")):
        r = convert_csv_row(row)
        records.append(r)

    add_backing_ids(records)

    with open(output_file, "w") as out:
        json.dump(records, out)

    print("Wrote %d records" % len(records))
