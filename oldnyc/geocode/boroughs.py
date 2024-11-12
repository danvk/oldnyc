"""Utility for mapping a lat/lon to a borough."""

import json
import re

from oldnyc.geocode import shape_utils
from oldnyc.ingest.util import BOROUGHS
from oldnyc.item import Item

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
