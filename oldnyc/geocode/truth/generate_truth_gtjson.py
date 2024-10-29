#!/usr/bin/env python
"""Generate truth GTJSON from the localturk CSV output and NYPL surveyor.geojson."""

import csv
import json
import sys
from typing import Any

import pygeojson

from oldnyc.item import load_items

if __name__ == "__main__":
    id_to_data: dict[str, tuple[pygeojson.Point | None, Any]] = {}
    prev_ids = set()
    for row in csv.DictReader(open("data/geocode/truth.csv")):
        id_ = row["id"]
        if id_ in prev_ids:
            raise ValueError(f"Duplicate ID: {id_}")
        prev_ids.add(id_)
        is_locatable = row["geolocatable"] == "Locatable"

        geometry: pygeojson.Point | None = None
        if is_locatable:
            (lat, lng) = (float(x) for x in json.loads(row["latLng"])["latLng"].split(","))
            geometry = pygeojson.Point((lng, lat))

        id_to_data[id_] = (geometry, row)

    localturk_features: list[pygeojson.Feature] = []
    for id_, entry in id_to_data.items():
        geometry, row = entry

        localturk_features.append(
            pygeojson.Feature(
                geometry=geometry,
                id=id_,
                properties={
                    "title": row["title"],
                    "url": row["url"],
                    "source": "localturk",
                    "geocoding_notes": row["user_notes"],
                },
            )
        )

    # Pull in truth data from NYPL surveyor.geojson.
    # This contains images from other collections, so we have to filter and join it.
    items = load_items("data/images.ndjson")
    uuid_to_item = {item.url.split("/")[-1]: item for item in items}
    surveyor = pygeojson.load_feature_collection(open("data/geocode/surveyor.geojson"))
    surveyor_features: list[pygeojson.Feature] = []
    for f in surveyor.features:
        id = f.properties["id"].replace("nypl-", "")
        item = uuid_to_item.get(id)
        if not item:
            continue
        geom = f.geometry
        if isinstance(geom, pygeojson.GeometryCollection):
            # The second entry is a bearing, which is overkill for OldNYC.
            geom = geom.geometries[0]
            assert isinstance(geom, pygeojson.Point)
        assert isinstance(geom, pygeojson.Point)
        props = f.properties
        date = None
        if "validSince" in props and "validUntil" in props:
            date = (props["validSince"], props["validUntil"])
        if item.id in prev_ids:
            raise ValueError(f"Duplicate ID: {item.id}")
        prev_ids.add(item.id)
        surveyor_features.append(
            pygeojson.Feature(
                geometry=geom,
                id=item.id,
                properties={
                    "title": item.title,
                    "url": item.url,
                    "date": date,
                    "source": "surveyor",
                    "surveyor_data": props,
                },
            )
        )

    all_features = localturk_features + surveyor_features
    all_features.sort(key=lambda f: str(f.id))
    fc = pygeojson.FeatureCollection(all_features)
    # fc = pygeojson.FeatureCollection(surveyor_features)
    # workaround for https://github.com/hawkaa/pygeojson/issues/18
    out = json.loads(pygeojson.dumps(fc))
    for f in out["features"]:
        if "geometry" not in f:
            f["geometry"] = None
    print(json.dumps(out, indent=2))

    sys.stderr.write(f"Generated {len(fc.features)} truth features:\n")
    sys.stderr.write(f"  {len(localturk_features)} from localturk\n")
    sys.stderr.write(f"  {len(surveyor_features)} from surveyor\n")
