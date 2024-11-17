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
    assert_close(grid.code("5", "100"), (40.790469, -73.953898))


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

    assert grid.parse_street_ave("West 98th Street", "Central Park West") == ("8", "98")

    # assert grid.parse_street_ave("Lenox Ave", "140-141 Sts") == ("6", "140")
    assert grid.parse_street_ave("Fifth Avenue", "100th Street") == ("5", "100")

    assert grid.parse_street_ave("Broadway", "59th Street") == ("Broadway", "59")
    # assert grid.parse_street_ave("St. Nicholas Avenue", "147th Street") == (
    #     "St. Nicholas Avenue",
    #     "147",
    # )


def test_geocode_broadway():
    # this is an exact intersection
    assert_close(grid.geocode_intersection("Broadway", "59th Street"), (40.767696, -73.981679))
    # these are interpolations
    assert_close(grid.geocode_intersection("Broadway", "24"), (40.7422035, -73.989151))
    assert_close(grid.geocode_intersection("Broadway", "124"), (40.8140625, -73.959421))
    # this isn't great, but probably not too far off the intended location.
    assert_close(grid.geocode_intersection("Broadway", "127"), (40.816311, -73.957802))


def test_geocode_above_125():
    assert_close(grid.geocode_intersection("7th Avenue", "134th Street"), (40.8146691, -73.94419))


def test_parse_ave():
    assert grid.parse_ave("Broadway") == "Broadway"
    assert grid.parse_ave("Fifth Avenue") == "5"
    assert grid.parse_ave("Avenue A") == "A"
    assert grid.parse_ave("Central Park West") == "Central Park West"
