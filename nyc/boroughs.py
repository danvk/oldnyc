"""Utility for mapping a lat/lon to a borough."""

import json
import nyc.shape_utils as shape_utils
import re
import os
import sys

boroughs = None
neighborhoods = None
_neighborhood_cache = {}


def _getBoroughJsonPath():
    for path in ["borough-polygons.json", "nyc/borough-polygons.json"]:
        if os.path.exists(path):
            return path
    raise Exception("Couldn't find borough-polygons.json file.")


def _getNeighborhoodJsonPath():
    for path in ["neighborhood-polygons.json", "nyc/neighborhood-polygons.json"]:
        if os.path.exists(path):
            return path
    raise Exception("Couldn't find neighborhood-polygons.json file.")


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


def PointToNeighborhood(lat, lon):
    """Returns the name of a neighborhood, or None if the point is not in NYC."""
    global neighborhoods
    if not neighborhoods:
        neighborhoods = json.load(open(_getNeighborhoodJsonPath()))

    pt = (lon, lat)
    if pt in _neighborhood_cache:
        return _neighborhood_cache[pt]

    for k, v in neighborhoods.iteritems():
        if shape_utils.PointInPolygon(pt, v):
            _neighborhood_cache[pt] = k
            return k

    # Check if it's _really_ close to a neighborhood.
    # This can happen when a boundary road between neighborhoods isn't included
    # in them.
    # The 0.0001 = 1e-4 comes from the distance from (8th ave, 58th street) to:
    # Hell's Kitchen:  1.85e-05
    # Upper West Side: 4.71e-06
    for k, v in neighborhoods.iteritems():
        d = shape_utils.DistanceToPolygon(pt, v)
        if d < 0.0002:
            _neighborhood_cache[pt] = k
            return k

    sys.stderr.write("minDist to (%s, %s) = %f\n" % (lat, lon, d))
    _neighborhood_cache[pt] = None
    return None


if __name__ == "__main__":
    re.match()
