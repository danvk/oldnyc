#!/usr/bin/env python
"""Various output formats for generate-geocodes.py."""

import json
import sys
from collections import defaultdict
from json import encoder
from typing import Sequence

from oldnyc.geocode import record
from oldnyc.geocode.geocode_types import Locatable, Location
from oldnyc.item import Item

encoder.FLOAT_REPR = lambda o: format(o, ".6f")  # type: ignore


# could be tuple[Item, None, None] | tuple[Item, str, Location | Locatable]
LocatedRecord = tuple[Item, str | None, Location | Locatable | None]


def _generateJson(located_recs: Sequence[LocatedRecord], lat_lon_map: dict[str, str]):
    out: dict[str, list[str]] = {}
    # "lat,lon" -> list of items
    ll_to_id: dict[str, list[Item]] = defaultdict(list)

    claimed_in_map = {}

    for r, _coder, location_data in located_recs:
        if not location_data:
            continue
        lat, lon = location_data.get("lat"), location_data.get("lon")
        assert lat is not None
        assert lon is not None
        ll_str = "%.6f,%.6f" % (lat, lon)
        if lat_lon_map and ll_str in lat_lon_map:
            claimed_in_map[ll_str] = True
            ll_str = lat_lon_map[ll_str]
        ll_to_id[ll_str].append(r)

    # print len(claimed_in_map)
    # print len(lat_lon_map)
    # assert len(claimed_in_map) == len(lat_lon_map)

    no_date = 0
    points = 0
    photos = 0
    for lat_lon, recs in ll_to_id.items():
        rec_dates = [(r, record.get_date_range(r.date or "")) for r in recs]
        # XXX the "if" filter here probably doesn't do anything
        sorted_recs = sorted(
            [rdr for rdr in rec_dates if rdr[1] and rdr[1][1]],
            key=lambda rdr: rdr[1][1],
        )
        no_date += len(recs) - len(sorted_recs)

        out_recs = [r.id for r, _ in sorted_recs]
        if out_recs:
            points += 1
            photos += len(out_recs)
            out[lat_lon] = out_recs

    sys.stderr.write("Dropped w/ no date: %d\n" % no_date)
    sys.stderr.write("Unique lat/longs: %d\n" % points)
    sys.stderr.write("Total photographs: %d\n" % photos)

    return out


def printJsonNoYears(located_recs: list[LocatedRecord], lat_lon_map: dict[str, str]):
    ll_to_items = _generateJson(located_recs, lat_lon_map)
    print("var lat_lons = ")
    print(json.dumps(ll_to_items, sort_keys=True))


def printIdLocation(located_recs: list[LocatedRecord]):
    for r, coder, location_data in located_recs:
        if location_data:
            lat, lng = location_data.get("lat"), location_data.get("lon")
            loc = (str((lat, lng)) or "") + "\t" + location_data["address"]
        else:
            loc = "n/a\tn/a"

        print("\t".join([r.id, coder or "failed", loc]))


def output_geojson(located_recs: list[LocatedRecord], all_recs: list[Item]):
    features = []
    id_to_loc = {rec[0].id: rec for rec in located_recs}
    for r in all_recs:
        _, coder, location_data = id_to_loc[r.id]
        feature = {
            "id": r.id,
            "type": "Feature",
            "geometry": (
                {
                    "type": "Point",
                    "coordinates": [location_data["lon"], location_data["lat"]],  # type: ignore
                }
                if location_data
                else None
            ),
            "properties": {
                "title": r.title,
                "date": r.date,
                "geocode": (
                    {
                        "technique": coder,
                        "lat": location_data["lat"],  # type: ignore
                        "lng": location_data["lon"],  # type: ignore
                        **location_data,
                    }
                    if location_data
                    else None
                ),
                "image": {
                    "url": f"http://images.nypl.org/?id={r.id}&t=w",
                    "thumb_url": f"http://images.nypl.org/?id={r.id}&t=w",
                },
                "url": r.url,
                "nypl_fields": {"alt_title": r.alt_title, "address": r.address},
            },
        }
        features.append(feature)

    print(
        json.dumps(
            {"type": "FeatureCollection", "features": features},
            indent=2,
            sort_keys=True,
        )
    )
