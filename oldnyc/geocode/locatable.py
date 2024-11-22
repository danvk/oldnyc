# From title_pattern.py


import sys
from typing import Any

from oldnyc.geocode import grid
from oldnyc.geocode.boroughs import point_to_borough
from oldnyc.geocode.geocode_types import (
    AddressLocation,
    IntersectionLocation,
    LatLngLocation,
    Locatable,
    Point,
)
from oldnyc.item import Item


def locate_with_osm(r: Item, loc: Locatable) -> Point | None:
    """Extract a location from a Locatable, without going to Google."""
    if isinstance(loc, LatLngLocation):
        return round(loc.lat, 7), round(loc.lng, 7)
    elif isinstance(loc, AddressLocation):
        return None  # not implemented yet
    # Must be an intersection
    assert isinstance(loc, IntersectionLocation)

    str1 = loc.str1
    str2 = loc.str2
    boro = loc.boro
    if boro not in ("Manhattan", "New York"):
        return None
    try:
        ave, street = grid.parse_street_ave(str1, str2)
        pt = grid.code(ave, street)
    except ValueError:
        # sys.stderr.write(f"grid fail\t{r.id}\t{loc}\n")
        return None
    if not pt:
        return None
    lat, lng = pt
    return round(float(lat), 7), round(float(lng), 7)  # they're numpy floats


def get_address_for_google(loc: Locatable) -> str:
    if isinstance(loc, AddressLocation):
        return f"{loc.num} {loc.street}, {loc.boro}, NY"
    elif isinstance(loc, IntersectionLocation):
        return f"{loc.str1} and {loc.str2}, {loc.boro}, NY"
    else:
        raise ValueError()


def extract_point_from_google_geocode(
    geocode: dict[str, Any], loc: Locatable, record: Item
) -> Point | None:
    if isinstance(loc, LatLngLocation):
        return loc.lat, loc.lng
    elif isinstance(loc, AddressLocation):
        pt = get_lat_lng_from_geocode(geocode, ["street_address", "premise"])
    elif isinstance(loc, IntersectionLocation):
        pt = get_lat_lng_from_geocode(geocode, ["intersection"])
    else:
        raise ValueError()

    if not pt:
        return None
    lat, lng = pt
    geocode_boro = point_to_borough(lat, lng)
    boro = loc.boro if loc.boro != "New York" else "Manhattan"
    if geocode_boro != boro:
        # self.n_boro_mismatch += 1
        sys.stderr.write(
            f"Borough mismatch: {record.id}: {loc.source} geocoded to {geocode_boro} not {boro}\n"
        )
        return None
    # self.n_success += 1
    return pt


def get_lat_lng_from_geocode(geocode: dict[str, Any], desired_types: list[str]) -> Point | None:
    """Extract a location from a Google Maps geocoding API response if it has the expected type."""
    for data_type in desired_types:
        # N = len(geocode["results"])
        for i, result in enumerate(geocode["results"]):
            # partial matches tend to be inaccurate.
            # if result.get('partial_match'): continue
            # data['type'] is something like 'address' or 'intersection'.
            if data_type in result["types"]:
                # sys.stderr.write(f"Match on {i} / {N}: {result}\n")
                loc = result["geometry"]["location"]
                return (loc["lat"], loc["lng"])
