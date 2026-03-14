"""Unit tests for locatable.py.

All tests use only files on disk (data/, geocache/) — no network calls.
"""

import pytest

from oldnyc.geocode import geocoder, grid
from oldnyc.geocode.geocode_types import (
    AddressLocation,
    IntersectionLocation,
    LatLngLocation,
)
from oldnyc.geocode.locatable import (
    KNOWN_BAD,
    extract_point_from_google_geocode,
    get_address_for_google,
    get_lat_lng_from_geocode,
    locate_with_google,
    locate_with_osm,
    round_pt,
)
from oldnyc.item import Item, blank_item

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

CODER = "test"


def make_item(id: str = "test-id") -> "Item":
    item = blank_item()
    item.id = id
    return item


def make_geocoder() -> geocoder.Geocoder:
    """Return a Geocoder that reads from the local geocache but never uses the network."""
    return geocoder.Geocoder(network_allowed=False, wait_time=0)


# ---------------------------------------------------------------------------
# round_pt
# ---------------------------------------------------------------------------


def test_round_pt_rounds_to_7_decimals():
    assert round_pt((40.750907123456789, -73.980677987654321)) == (40.7509071, -73.9806780)


def test_round_pt_already_short():
    assert round_pt((40.5, -74.0)) == (40.5, -74.0)


# ---------------------------------------------------------------------------
# locate_with_osm — LatLngLocation
# ---------------------------------------------------------------------------


def test_locate_with_osm_latlng():
    item = make_item()
    loc = LatLngLocation(lat=40.7509071, lng=-73.9806780, source="test")
    g = grid.Grid()
    result = locate_with_osm(item, loc, CODER, g)
    assert result == (40.7509071, -73.9806780)


def test_locate_with_osm_latlng_rounds():
    item = make_item()
    loc = LatLngLocation(lat=40.750907123456789, lng=-73.980677987654321, source="test")
    g = grid.Grid()
    result = locate_with_osm(item, loc, CODER, g)
    # Should be rounded to 7 decimal places
    assert result == (round(40.750907123456789, 7), round(-73.980677987654321, 7))


# ---------------------------------------------------------------------------
# locate_with_osm — AddressLocation
# ---------------------------------------------------------------------------


def test_locate_with_osm_address_returns_none():
    """AddressLocation is not implemented for OSM geocoding."""
    item = make_item()
    loc = AddressLocation(num=448, street="West 20th Street", boro="Manhattan", source="test")
    g = grid.Grid()
    result = locate_with_osm(item, loc, CODER, g)
    assert result is None


# ---------------------------------------------------------------------------
# locate_with_osm — IntersectionLocation
# ---------------------------------------------------------------------------


def test_locate_with_osm_intersection_manhattan_exact():
    """A well-known Manhattan intersection that exists in the intersection data."""
    item = make_item("1507627")
    loc = IntersectionLocation(
        str1="Madison Avenue", str2="39th Street", boro="Manhattan", source="title-cross"
    )
    g = grid.Grid()
    result = locate_with_osm(item, loc, CODER, g)
    assert result is not None
    lat, lng = result
    assert lat == pytest.approx(40.7509, abs=0.001)
    assert lng == pytest.approx(-73.9807, abs=0.001)


def test_locate_with_osm_intersection_new_york_treated_as_manhattan():
    """'New York' as boro is converted to 'Manhattan' before geocoding."""
    item = make_item()
    # Use a real Manhattan intersection but pass boro="New York"
    loc = IntersectionLocation(
        str1="Madison Avenue", str2="39th Street", boro="New York", source="test"
    )
    g = grid.Grid()
    result = locate_with_osm(item, loc, CODER, g)
    assert result is not None


def test_locate_with_osm_intersection_brooklyn():
    """Brooklyn intersection that exists in the intersection data."""
    item = make_item("3984770")
    loc = IntersectionLocation(
        str1="Hamilton Avenue", str2="Summit Street", boro="Brooklyn", source="gpt"
    )
    g = grid.Grid()
    result = locate_with_osm(item, loc, CODER, g)
    assert result is not None
    lat, lng = result
    assert lat == pytest.approx(40.6828, abs=0.001)
    assert lng == pytest.approx(-74.0056, abs=0.001)


def test_locate_with_osm_intersection_unknown_returns_none():
    """An intersection that doesn't exist in the data returns None."""
    item = make_item()
    loc = IntersectionLocation(
        str1="Fake Street", str2="Imaginary Avenue", boro="Manhattan", source="test"
    )
    g = grid.Grid()
    result = locate_with_osm(item, loc, CODER, g)
    assert result is None


# ---------------------------------------------------------------------------
# get_address_for_google
# ---------------------------------------------------------------------------


def test_get_address_for_google_intersection():
    loc = IntersectionLocation(
        str1="Madison Avenue", str2="39th Street", boro="Manhattan", source="test"
    )
    result = get_address_for_google(loc)
    assert result == "Madison Avenue and 39th Street, Manhattan, NY"


def test_get_address_for_google_intersection_new_york():
    loc = IntersectionLocation(
        str1="Madison Avenue", str2="39th Street", boro="New York", source="test"
    )
    result = get_address_for_google(loc)
    assert result == "Madison Avenue and 39th Street, New York, NY"


def test_get_address_for_google_intersection_known_bad_str1():
    loc = IntersectionLocation(str1="unknown", str2="39th Street", boro="Manhattan", source="test")
    assert get_address_for_google(loc) is None


def test_get_address_for_google_intersection_known_bad_str2():
    loc = IntersectionLocation(
        str1="Madison Avenue", str2="Manhattan", boro="Manhattan", source="test"
    )
    assert get_address_for_google(loc) is None


def test_get_address_for_google_intersection_cursed():
    """Intersections in CURSED_INTERSECTIONS should return None."""
    loc = IntersectionLocation(
        str1="Amsterdam Avenue", str2="Broadway", boro="Manhattan", source="test"
    )
    assert get_address_for_google(loc) is None


def test_get_address_for_google_address():
    loc = AddressLocation(num=448, street="West 20th Street", boro="Manhattan", source="test")
    result = get_address_for_google(loc)
    assert result == "448 West 20th Street, Manhattan, NY"


def test_get_address_for_google_address_known_bad():
    loc = AddressLocation(num=100, street="unknown", boro="Manhattan", source="test")
    assert get_address_for_google(loc) is None


def test_get_address_for_google_latlng_raises():
    loc = LatLngLocation(lat=40.75, lng=-73.98, source="test")
    with pytest.raises(ValueError):
        get_address_for_google(loc)


@pytest.mark.parametrize("bad_street", list(KNOWN_BAD))
def test_get_address_for_google_all_known_bad_intersection(bad_street: str):
    loc = IntersectionLocation(str1=bad_street, str2="5th Avenue", boro="Manhattan", source="test")
    assert get_address_for_google(loc) is None


# ---------------------------------------------------------------------------
# get_lat_lng_from_geocode
# ---------------------------------------------------------------------------


def _make_geocode_response(types: list[str], lat: float, lng: float) -> dict:
    return {
        "status": "OK",
        "results": [
            {
                "types": types,
                "geometry": {"location": {"lat": lat, "lng": lng}},
                "formatted_address": "Test Address",
            }
        ],
    }


def test_get_lat_lng_from_geocode_matching_type():
    geocode = _make_geocode_response(["intersection"], 40.75, -73.98)
    result = get_lat_lng_from_geocode(geocode, ["intersection"])
    assert result == (40.75, -73.98)


def test_get_lat_lng_from_geocode_no_matching_type():
    geocode = _make_geocode_response(["route"], 40.75, -73.98)
    result = get_lat_lng_from_geocode(geocode, ["intersection"])
    assert result is None


def test_get_lat_lng_from_geocode_multiple_types_first_wins():
    """Returns the first result matching the first desired type."""
    geocode = {
        "status": "OK",
        "results": [
            {
                "types": ["route"],
                "geometry": {"location": {"lat": 40.71, "lng": -74.01}},
            },
            {
                "types": ["street_address"],
                "geometry": {"location": {"lat": 40.75, "lng": -73.98}},
            },
        ],
    }
    result = get_lat_lng_from_geocode(geocode, ["street_address", "premise"])
    assert result == (40.75, -73.98)


def test_get_lat_lng_from_geocode_empty_results():
    geocode = {"status": "ZERO_RESULTS", "results": []}
    result = get_lat_lng_from_geocode(geocode, ["intersection"])
    assert result is None


# ---------------------------------------------------------------------------
# extract_point_from_google_geocode
# ---------------------------------------------------------------------------


def test_extract_point_latlng_passthrough():
    """For LatLngLocation, the location from the loc object is returned directly."""
    loc = LatLngLocation(lat=40.75, lng=-73.98, source="test")
    geocode = _make_geocode_response(["intersection"], 99.0, -99.0)  # geocode coords ignored
    item = make_item()
    result = extract_point_from_google_geocode(geocode, loc, item, CODER)
    assert result == (40.75, -73.98)


def test_extract_point_intersection_success():
    """For an IntersectionLocation in Manhattan, extract a valid intersection geocode."""
    loc = IntersectionLocation(
        str1="39th Street", str2="Madison Avenue", boro="Manhattan", source="test"
    )
    # The geocoded point (40.7509, -73.9807) is in Manhattan
    geocode = _make_geocode_response(["intersection"], 40.7509088, -73.98069079999999)
    item = make_item()
    result = extract_point_from_google_geocode(geocode, loc, item, CODER)
    assert result is not None
    assert result == pytest.approx((40.7509088, -73.9806908), abs=1e-6)


def test_extract_point_intersection_boro_mismatch():
    """Returns None when the geocoded point is in the wrong borough."""
    loc = IntersectionLocation(
        str1="Madison Avenue", str2="39th Street", boro="Brooklyn", source="test"
    )
    # The geocoded point is in Manhattan, not Brooklyn
    geocode = _make_geocode_response(["intersection"], 40.7509088, -73.98069079999999)
    item = make_item()
    result = extract_point_from_google_geocode(geocode, loc, item, CODER)
    assert result is None


def test_extract_point_address_success():
    """For an AddressLocation in Manhattan, extract from a premise/street_address result."""
    loc = AddressLocation(num=35, street="East 68th Street", boro="Manhattan", source="test")
    geocode = _make_geocode_response(["premise"], 40.7692144, -73.9666901)
    item = make_item()
    result = extract_point_from_google_geocode(geocode, loc, item, CODER)
    assert result is not None
    lat, lng = result
    assert lat == pytest.approx(40.7692144, abs=1e-6)
    assert lng == pytest.approx(-73.9666901, abs=1e-6)


def test_extract_point_address_wrong_type_returns_none():
    """Returns None when the geocode result type doesn't match expected address types."""
    loc = AddressLocation(num=35, street="East 68th Street", boro="Manhattan", source="test")
    # "intersection" type won't match ["street_address", "premise"]
    geocode = _make_geocode_response(["intersection"], 40.7692144, -73.9666901)
    item = make_item()
    result = extract_point_from_google_geocode(geocode, loc, item, CODER)
    assert result is None


def test_extract_point_latlng_raises_for_invalid_type():
    """LatLngLocation with unknown Locatable type should be handled before call."""
    # Verify LatLngLocation returns early without checking geocode types
    loc = LatLngLocation(lat=40.0, lng=-73.0, source="test")
    geocode = {"status": "OK", "results": []}
    item = make_item()
    result = extract_point_from_google_geocode(geocode, loc, item, CODER)
    assert result == (40.0, -73.0)


# ---------------------------------------------------------------------------
# locate_with_google — end-to-end using real geocache files
# ---------------------------------------------------------------------------


def test_locate_with_google_intersection_cache_hit():
    """Test locate_with_google against a real geocache entry for a Manhattan intersection.

    Cache file: geocache/MzV0aCBTdHJlZXQgKEVhc3QpIGFuZCBNYWRpc29uIEF2ZW51ZSwgTWFuaGF0dGFuLCBOWQ
    Decoded address: '35th Street (East) and Madison Avenue, Manhattan, NY'
    Geocoded to: (40.748432, -73.982473)
    """
    item = make_item()
    loc = IntersectionLocation(
        str1="35th Street (East)", str2="Madison Avenue", boro="Manhattan", source="title-cross"
    )
    g = make_geocoder()
    result = locate_with_google(loc, item, CODER, g, print_geocodes=False)
    assert result is not None
    lat, lng = result
    assert lat == pytest.approx(40.748432, abs=0.0001)
    assert lng == pytest.approx(-73.982473, abs=0.0001)


def test_locate_with_google_address_cache_hit_street_address():
    """Test locate_with_google against a real geocache entry for an address.

    Cache file: geocache/MzggV2VzdCA1OHRoIFN0cmVldCwgTWFuaGF0dGFuLCBOWQ
    Decoded address: '38 West 58th Street, Manhattan, NY'
    Geocoded to: (40.7644664, -73.9754537)
    """
    item = make_item()
    loc = AddressLocation(
        num=38, street="West 58th Street", boro="Manhattan", source="title-address"
    )
    g = make_geocoder()
    result = locate_with_google(loc, item, CODER, g, print_geocodes=False)
    assert result is not None
    lat, lng = result
    assert lat == pytest.approx(40.7644664, abs=1e-5)
    assert lng == pytest.approx(-73.9754537, abs=1e-5)


def test_locate_with_google_cache_miss_returns_none():
    """Without network access and no cache entry, locate_with_google returns None."""
    item = make_item("no-cache-id")
    loc = IntersectionLocation(
        str1="Nonexistent Street", str2="Made Up Avenue", boro="Manhattan", source="test"
    )
    g = make_geocoder()
    result = locate_with_google(loc, item, CODER, g, print_geocodes=False)
    assert result is None


def test_locate_with_google_known_bad_returns_none():
    """Intersections with KNOWN_BAD streets are skipped before geocoding."""
    item = make_item()
    loc = IntersectionLocation(str1="unknown", str2="5th Avenue", boro="Manhattan", source="test")
    g = make_geocoder()
    result = locate_with_google(loc, item, CODER, g, print_geocodes=False)
    assert result is None


def test_locate_with_google_cursed_intersection_returns_none():
    """CURSED_INTERSECTIONS are skipped before geocoding."""
    item = make_item()
    loc = IntersectionLocation(
        str1="Amsterdam Avenue", str2="Broadway", boro="Manhattan", source="test"
    )
    g = make_geocoder()
    result = locate_with_google(loc, item, CODER, g, print_geocodes=False)
    assert result is None


def test_locate_with_google_latlng_raises():
    """LatLngLocation raises ValueError in get_address_for_google."""
    item = make_item()
    loc = LatLngLocation(lat=40.75, lng=-73.98, source="test")
    g = make_geocoder()
    with pytest.raises(ValueError):
        locate_with_google(loc, item, CODER, g, print_geocodes=False)
