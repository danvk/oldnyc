# From title_pattern.py


from collections import Counter, defaultdict
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

# (coder, event) -> count
counts = defaultdict[str, Counter[str]](Counter)


def round_pt(pt: Point) -> Point:
    lat, lng = pt
    return round(lat, 7), round(lng, 7)


def locate_with_osm(
    r: Item, loc: Locatable, coder: str, grid_geocoder: grid.GridGeocoder
) -> Point | None:
    """Extract a location from a Locatable, without going to Google."""
    if isinstance(loc, LatLngLocation):
        return round(loc.lat, 7), round(loc.lng, 7)
    elif isinstance(loc, AddressLocation):
        return None  # not implemented yet
    # Must be an intersection
    assert isinstance(loc, IntersectionLocation)

    boro = loc.boro
    boro = "Manhattan" if boro == "New York" else boro
    try:
        counts[coder]["grid: attempt"] += 1
        pt = grid_geocoder.geocode_intersection(loc.str1, loc.str2, boro, r.id)
    except ValueError:
        # sys.stderr.write(f"grid fail\t{r.id}\t{loc}\n")
        return None
    if not pt:
        return None
    counts[coder]["grid: success"] += 1
    return round_pt(pt)


KNOWN_BAD = {
    "Hudson River",
    "East River",
    "unknown",
    "Harlem River",
    "Manhattan",
    "West",
    "North",
    "East",
    "South",
    "Richmond",
    "docks",
    "Triborough Bridge",
    "Randall's Island",
    "Tottenville",
}
# 2986 -> 2719


def get_address_for_google(loc: Locatable) -> str | None:
    if isinstance(loc, AddressLocation):
        if loc.street in KNOWN_BAD:
            return None
        return f"{loc.num} {loc.street}, {loc.boro}, NY"
    elif isinstance(loc, IntersectionLocation):
        if loc.str1 in KNOWN_BAD or loc.str2 in KNOWN_BAD:
            return None
        return f"{loc.str1} and {loc.str2}, {loc.boro}, NY"
    else:
        raise ValueError()


def extract_point_from_google_geocode(
    geocode: dict[str, Any], loc: Locatable, record: Item, coder: str
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
        counts[coder]["google: fail"] += 1
        return None
    lat, lng = pt
    geocode_boro = point_to_borough(lat, lng)
    boro = loc.boro if loc.boro != "New York" else "Manhattan"
    if geocode_boro != boro:
        # self.n_boro_mismatch += 1
        # sys.stderr.write(
        #     f"Borough mismatch: {record.id}: {loc.source} geocoded to {geocode_boro} not {boro}\n"
        # )
        counts[coder]["google: boro mismatch"] += 1
        return None
    # TODO: track hits by locatable type
    counts[coder]["google: success"] += 1
    return round_pt(pt)


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
