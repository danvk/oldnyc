import pytest

from oldnyc.geocode import grid


def assert_close(ll1: tuple[float, float] | None, ll2: tuple[float, float]):
    """Assert that two latitude & longitude tuples are "close"."""
    assert ll1 is not None
    assert ll1[0] == pytest.approx(ll2[0], 1e-6)
    assert ll1[1] == pytest.approx(ll2[1], 1e-6)


def test_exact():
    # It's really Park Avenue South.
    assert_close(grid.code("4", "17"), (40.736518, -73.988962))


def test_interpolate():
    # This is halfway between 26th & 28th.
    assert_close(grid.code("9", "27"), (40.749020, -73.9995210))


def test_extrapolate():
    assert_close(grid.code("A", "15"), (40.731083, -73.979847))
    assert_close(grid.code("A", "20"), (40.734071, -73.977654))


def test_may_extrapolate():
    assert grid.may_extrapolate("A", "15")
    assert grid.may_extrapolate("2", "8")
    assert grid.may_extrapolate("A", "25")
    assert not grid.may_extrapolate("4", "8")
    assert not grid.may_extrapolate("D", "25")
    assert not grid.may_extrapolate("7", "10")
    assert not grid.may_extrapolate("B", "93")  # 723557f-c


def test_parse_street_ave():
    assert grid.parse_street_ave("122nd St", "1st Ave") == ("1", "122")
    assert grid.parse_street_ave("1st Ave", "122nd St") == ("1", "122")
    assert grid.parse_street_ave("18th Street", "Avenue A") == ("A", "18")
    assert grid.parse_street_ave("18th Street (West)", "4th Avenue") == ("4", "18")

    # 711722f
    assert grid.parse_street_ave("9th Avenue", "23rd Street (West)") == ("9", "23")

    # 464848
    assert grid.parse_street_ave("West End Avenue", "106th Street") == ("11", "106")
    assert grid.parse_street_ave("Stanley Court, corner West End Avenue", "106th Street") == (
        "11",
        "106",
    )
