"""Utility for mapping a lat/lon to a borough."""

import json
import os

import nyc.shape_utils as shape_utils

boroughs = None


def _getBoroughJsonPath():
    for path in ["borough-polygons.json", "nyc/borough-polygons.json"]:
        if os.path.exists(path):
            return path
    raise Exception("Couldn't find borough-polygons.json file.")


def PointToBorough(lat, lon):
    """Returns the name of a borough, or None if the point is not in NYC.

    Possible return values are:
    'Bronx', 'Brooklyn', 'Staten Island', 'Manhattan', 'Queens', None
    """
    global boroughs
    if not boroughs:
        boroughs = json.load(open(_getBoroughJsonPath()))

    pt = (lon, lat)
    for k, v in boroughs.items():
        if shape_utils.PointInPolygon(pt, v):
            return k
    return None
