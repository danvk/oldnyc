#!/usr/bin/env python
"""Various output formats for generate-geocodes.py."""

import dataclasses
import json
import sys
from datetime import date
from json import encoder
from typing import Sequence

from oldnyc.geocode.geocode_types import GeocodedItem
from oldnyc.geocode.locatable import locatable_to_dict
from oldnyc.ingest.dates import extract_years
from oldnyc.item import Item
from oldnyc.site.site_data_type import GeoJsonFeature, GeoJsonProperties
from oldnyc.util import remove_empty

encoder.FLOAT_REPR = lambda o: format(o, ".6f")  # type: ignore


def get_date_range(date_str: str) -> tuple[date, date]:
    # TODO: this is a bit wonky; could use clean_date more directly.
    years = extract_years(date_str)
    if not years or years == [""]:
        return date(1850, 1, 1), date(1999, 12, 31)
    dates = [date(int(y), 1, 1) for y in years]
    return min(dates), max(dates)


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


def output_geojson(
    located_recs: Sequence[GeocodedItem], all_recs: list[Item], lat_lon_map: dict[str, str]
):
    features: list[GeoJsonFeature] = []
    id_to_geocode = {r.item.id: r for r in located_recs}
    for r in all_recs:
        geocode = id_to_geocode[r.id]
        result = geocode.result
        pt = result.lat_lon if result else None

        if pt and lat_lon_map:
            ll_str = "%.6f,%.6f" % pt
            if ll_str in lat_lon_map:
                ll_str = lat_lon_map[ll_str]
                lat, lng = [float(x) for x in ll_str.split(",")]
                pt = (lat, lng)

        props: GeoJsonProperties = {
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
            "url": r.url,
            "nypl_fields": remove_empty(
                {
                    "alt_title": r.alt_title,
                    "subjects": dataclasses.asdict(r.subject),
                }
            ),
        }
        if geocode.failures:
            props["geocode_failures"] = [
                {"technique": coder, **locatable_to_dict(loc)} for coder, loc in geocode.failures
            ]

        feature: GeoJsonFeature = {
            "id": r.id,
            "type": "Feature",
            "geometry": (
                {
                    "type": "Point",
                    "coordinates": (pt[1], pt[0]),
                }
                if pt
                else None
            ),
            "properties": props,
        }
        features.append(feature)

    points = {tuple(f["geometry"]["coordinates"]) for f in features if f["geometry"]}

    sys.stderr.write("Unique lat/longs: %d\n" % len(points))
    print(
        json.dumps(
            {"type": "FeatureCollection", "features": features},
            indent=2,
            sort_keys=True,
        )
    )
