#!/usr/bin/env python
"""Various output formats for generate-geocodes.py."""

import dataclasses
import json
import sys
from collections import defaultdict
from datetime import date
from json import encoder
from typing import Sequence

from oldnyc.geocode.geocode_types import Locatable, Point
from oldnyc.ingest.dates import extract_years
from oldnyc.item import Item

encoder.FLOAT_REPR = lambda o: format(o, ".6f")  # type: ignore


# could be tuple[Item, None, None] | tuple[Item, str, Location | Locatable]
LocatedRecord = tuple[Item, tuple[str, Locatable, Point] | None]


def get_date_range(date_str: str) -> tuple[date, date]:
    # TODO: this is a bit wonky; could use clean_date more directly.
    years = extract_years(date_str)
    if not years or years == [""]:
        return date(1850, 1, 1), date(1999, 12, 31)
    dates = [date(int(y), 1, 1) for y in years]
    return min(dates), max(dates)


def _generateJson(located_recs: Sequence[LocatedRecord], lat_lon_map: dict[str, str]):
    out: dict[str, list[str]] = {}
    # "lat,lon" -> list of items
    ll_to_id: dict[str, list[Item]] = defaultdict(list)

    claimed_in_map = {}

    for r, loc in located_recs:
        if not loc:
            continue
        (lat, lon) = loc[2]
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
        rec_dates = [(r, get_date_range(r.date or "")) for r in recs]
        sorted_recs = sorted(
            rec_dates,
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


def printJsonNoYears(located_recs: Sequence[LocatedRecord], lat_lon_map: dict[str, str]):
    ll_to_items = _generateJson(located_recs, lat_lon_map)
    print(json.dumps(ll_to_items, sort_keys=True))


def printIdLocation(located_recs: Sequence[LocatedRecord]):
    for r, loc_data in located_recs:
        coder = None
        if loc_data:
            coder, location_data, pt = loc_data
            lat, lng = pt
            loc = (str((lat, lng)) or "") + "\t" + location_data.source
        else:
            loc = "n/a\tn/a"

        print("\t".join([r.id, coder or "failed", loc]))


locatable_types = {
    "AddressLocation": "address",
    "IntersectionLocation": "intersection",
    "LatLngLocation": "point_of_interest",
}


def output_geojson(located_recs: Sequence[LocatedRecord], all_recs: list[Item]):
    features = []
    id_to_loc = {r.id: loc for r, loc in located_recs}
    for r in all_recs:
        loc_data = id_to_loc[r.id]
        coder, locatable, pt = loc_data or (None, None, None)
        feature = {
            "id": r.id,
            "type": "Feature",
            "geometry": (
                {
                    "type": "Point",
                    "coordinates": [pt[1], pt[0]],
                }
                if pt
                else None
            ),
            "properties": {
                "title": r.title,
                "date": r.date,
                "geocode": (
                    {
                        "technique": coder,
                        "lat": pt[0],
                        "lng": pt[1],
                        "type": locatable_types[locatable.__class__.__name__],
                        **dataclasses.asdict(locatable),
                    }
                    if pt and locatable
                    else None
                ),
                "image": {
                    "url": f"http://images.nypl.org/?id={r.id}&t=w",
                    "thumb_url": f"http://images.nypl.org/?id={r.id}&t=w",
                },
                "url": r.url,
                "nypl_fields": {"alt_title": r.alt_title},
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
