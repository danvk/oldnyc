#!/usr/bin/env python
"""TODO: what does this do? Can it be deleted?"""

import csv
import json
import sys

from oldnyc.geocode.boroughs import point_to_borough

if __name__ == "__main__":
    infile, outfile = sys.argv[1:]
    with open(outfile, "w") as out, open(infile, "r") as f:
        reader = csv.DictReader(f)
        writer = csv.DictWriter(out, fieldnames=([*(reader.fieldnames or [])] + ["borough"]))
        for i, row in enumerate(reader):
            if i == 0:
                writer.writeheader()

            location = row["location"] or "null"
            row["location"] = location
            if row["geolocatable"] == "Locatable" and not row["latLng"] and location != "null":
                lat, lng = json.loads(location)
                row["latLng"] = json.dumps({"latLng": f"{lat},{lng}"})
            if row["latLng"]:
                latLng = json.loads(row["latLng"])
                lat, lng = (float(x) for x in latLng["latLng"].split(","))
                borough = point_to_borough(lat, lng)
                row["borough"] = borough
            writer.writerow(row)
