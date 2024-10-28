#!/usr/bin/env python
"""Generate truth GTJSON from the localturk CSV output."""

import csv
import json

if __name__ == "__main__":
    id_to_data = {}
    prev_ids = set()
    for row in csv.DictReader(open("locatable_turk/truth.csv")):
        id_ = row["id"]
        if id_ in prev_ids:
            raise ValueError(f"Duplicate ID: {id_}")
        prev_ids.add(id_)
        is_locatable = row["geolocatable"] == "Locatable"

        geometry = None
        if is_locatable:
            (lat, lng) = (float(x) for x in json.loads(row["latLng"])["latLng"].split(","))
            geometry = {"type": "Point", "coordinates": [lng, lat]}

        id_to_data[id_] = (geometry, row)

    features = []
    for id_, entry in id_to_data.items():
        geometry, row = entry

        features.append(
            {
                "type": "Feature",
                "geometry": geometry,
                "id": id_,
                "properties": {
                    "title": row["title"],
                    "url": row["url"],
                    "geocoding_notes": row["user_notes"],
                },
            }
        )

    print(json.dumps({"type": "FeatureCollection", "features": features}))
