#!/usr/bin/env python
"""Various output formats for generate-geocodes.py."""

import json
import sys
from collections import defaultdict
from datetime import date
from json import encoder
from typing import Sequence

from oldnyc.geocode.geocode_types import GeocodedItem, Locatable, Point
from oldnyc.geocode.locatable import locatable_to_dict
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


def _generateJson(located_recs: Sequence[GeocodedItem], lat_lon_map: dict[str, str]):
    out: dict[str, list[str]] = {}
    # "lat,lon" -> list of items
    ll_to_id: dict[str, list[Item]] = defaultdict(list)

    claimed_in_map = {}

    for item in located_recs:
        if not item.result:
            continue
        ll_str = "%.6f,%.6f" % item.result.lat_lon
        if lat_lon_map and ll_str in lat_lon_map:
            claimed_in_map[ll_str] = True
            ll_str = lat_lon_map[ll_str]
        ll_to_id[ll_str].append(item.item)

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


def printJsonNoYears(located_recs: Sequence[GeocodedItem], lat_lon_map: dict[str, str]):
    ll_to_items = _generateJson(located_recs, lat_lon_map)
    print(json.dumps(ll_to_items, sort_keys=True))


def printIdLocation(located_recs: Sequence[GeocodedItem]):
    for item in located_recs:
        coder = None
        r = item.result
        if r:
            coder = r.coder
            loc = f"{r.lat_lon}\t{r.location.source}"
        else:
            loc = "n/a\tn/a"

        print("\t".join([item.item.id, coder or "failed", loc]))


locatable_types = {
    "AddressLocation": "address",
    "IntersectionLocation": "intersection",
    "LatLngLocation": "point_of_interest",
}


def output_geojson(located_recs: Sequence[GeocodedItem], all_recs: list[Item]):
    features = []
    id_to_geocode = {r.item.id: r for r in located_recs}
    for r in all_recs:
        geocode = id_to_geocode[r.id]
        result = geocode.result
        pt = result.lat_lon if result else None
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
                        "technique": result.coder,
                        "source": result.location.source,  # duplicative
                        "location": locatable_to_dict(result.location),
                        "geocoder": result.geocoder,
                    }
                    if result
                    else None
                ),
                **(
                    {
                        "geocode_failures": [
                            {"technique": coder, **locatable_to_dict(loc)}
                            for coder, loc in geocode.failures
                        ]
                    }
                    if geocode.failures
                    else {}
                ),
                # "image": {
                #     "url": f"http://images.nypl.org/?id={r.id}&t=w",
                #     "thumb_url": f"http://images.nypl.org/?id={r.id}&t=w",
                # },
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
