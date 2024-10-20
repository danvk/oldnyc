"""Utility for mapping a lat/lon to a borough."""

import json

from oldnyc.geocode import shape_utils

BOROUGHS_JSON_FILE = "data/originals/borough-polygons.json"

boroughs = None


def point_to_borough(lat: float, lon: float) -> str | None:
    """Returns the name of a borough, or None if the point is not in NYC.

    Possible return values are:
    'Bronx', 'Brooklyn', 'Staten Island', 'Manhattan', 'Queens', None
    """
    global boroughs
    if not boroughs:
        boroughs = json.load(open(BOROUGHS_JSON_FILE))

    pt = (lon, lat)
    for k, v in boroughs.items():
        if shape_utils.PointInPolygon(pt, v):
            return k
    return None
