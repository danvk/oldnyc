"""Utility for mapping a lat/lon to a borough."""

import json
import re

from oldnyc.geocode import shape_utils
from oldnyc.ingest.util import BOROUGHS
from oldnyc.item import Item

# TODO: convert this to GeoJSON
BOROUGHS_JSON_FILE = "data/originals/borough-polygons.json"

boroughs = None


def _get_boroughs():
    global boroughs
    if not boroughs:
        boroughs = json.load(open(BOROUGHS_JSON_FILE))
    return boroughs


def point_to_borough(lat: float, lon: float) -> str | None:
    """Returns the name of a borough, or None if the point is not in NYC.

    Possible return values are:
    'Bronx', 'Brooklyn', 'Staten Island', 'Manhattan', 'Queens', None
    """
    boroughs = _get_boroughs()

    pt = (lon, lat)
    for k, v in boroughs.items():
        if shape_utils.PointInPolygon(pt, v):
            return k
    return None


MANHATTAN_BBOX = ((-74.0235, 40.6987), (-73.906, 40.8799))


def is_in_manhattan(lat: float, lng: float) -> bool:
    """Same as point_to_borough(lat, lng) = "Manhattan", but faster."""
    if not (
        MANHATTAN_BBOX[0][0] <= lng <= MANHATTAN_BBOX[1][0]
        and MANHATTAN_BBOX[0][1] <= lat <= MANHATTAN_BBOX[1][1]
    ):
        return False
    boroughs = _get_boroughs()
    manhattan = boroughs["Manhattan"]
    return shape_utils.PointInPolygon((lng, lat), manhattan)


boroughs_pat = r"(?:Manhattan|Brooklyn|Queens|Bronx|Staten Island|Richmond)"
borough_re = re.compile(rf"\b({boroughs_pat})\b")


def guess_borough(item: Item):
    titles = [item.title] + item.alt_title
    for b in BOROUGHS:
        full = f"{b} (New York, N.Y.)"
        if full in item.subject.geographic:
            return b
        full = f"/ {b}"
        if item.source.endswith(full):
            return b
        for t in titles:
            if t.startswith(b):
                return b
    for t in titles:
        m = borough_re.search(t)
        if m:
            return m.group(1)
    return None
