#!/usr/bin/env python
"""Convert localturk output to a GeoJSON file."""

import csv
import json
import sys

import pygeojson

from oldnyc.geocode.coders.subjects import IGNORE_SUBJECTS


def main():
    (infile,) = sys.argv[1:]

    features: list[pygeojson.Feature] = []
    csv.field_size_limit(sys.maxsize)
    for row in csv.DictReader(open(infile)):
        geo = row["geo"]
        count = int(row["count"])
        outcome = row["outcome"]
        latlng = row["latlng"]
        result = row["result"]
        user_notes = row["user_notes"]
        specificity = int(row["specificity"])

        if result == "Good":
            coords = json.loads(latlng)
            features.append(
                pygeojson.Feature(
                    geometry=pygeojson.Point(coords),  # type: ignore
                    properties={
                        "geo": geo,
                        "count": count,
                        "source": "2024",
                        "result": result,
                        "user_notes": user_notes,
                        "specificity": specificity,
                    },
                )
            )

        elif outcome == "nyc_parks":
            (lat, lng) = (float(x) for x in latlng.split(","))
            features.append(
                pygeojson.Feature(
                    geometry=pygeojson.Point((lng, lat)),
                    properties={
                        "geo": geo,
                        "count": count,
                        "source": "2013",
                        "specificity": specificity,
                    },
                )
            )

        else:
            features.append(
                pygeojson.Feature(
                    geometry=None,
                    properties={
                        "geo": geo,
                        "count": count,
                        "source": "2024",
                        "result": result,
                        "user_notes": user_notes,
                        "specificity": 0,
                    },
                )
            )

    # TODO: move these into the CSV file
    for subject in sorted(IGNORE_SUBJECTS):
        features.append(
            pygeojson.Feature(
                geometry=None,
                properties={
                    "geo": subject,
                    "count": 0,
                    "source": "2024",
                    "result": "Too broad",
                    "user_notes": "",
                    "specificity": 0,
                },
            )
        )

    fc = pygeojson.FeatureCollection(features)
    # fc = pygeojson.FeatureCollection(surveyor_features)
    # workaround for https://github.com/hawkaa/pygeojson/issues/18
    out = json.loads(pygeojson.dumps(fc))
    for f in out["features"]:
        if "geometry" not in f:
            f["geometry"] = None
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
