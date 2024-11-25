import pytest

from oldnyc.geocode import grid
from oldnyc.geocode.grid import Grid

M = "Manhattan"


def assert_close(ll1: tuple[float, float] | None, ll2: tuple[float, float]):
    """Assert that two latitude & longitude tuples are "close"."""
    assert ll1 is not None
    assert ll1[0] == pytest.approx(ll2[0], 1e-6)
    assert ll1[1] == pytest.approx(ll2[1], 1e-6)


def test_exact():
    g = Grid()
    # It's really Park Avenue South.
    assert_close(g.code("4", "17"), (40.736518, -73.988962))


def test_interpolate():
    g = Grid()
    # This is halfway between 26th & 28th.
    assert_close(g.code("9", "27"), (40.749020, -73.9995210))
    assert_close(g.code("5", "100"), (40.790469, -73.953898))


def test_extrapolate():
    g = Grid()
    assert_close(g.code("A", "15"), (40.731083, -73.979847))
    assert_close(g.code("A", "20"), (40.734071, -73.977654))


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
    assert grid.parse_street_ave("St. Nicholas Avenue", "147th Street") == (
        "St. Nicholas Avenue",
        "147",
    )


def test_geocode_broadway():
    g = Grid()
    # this is an exact intersection
    assert_close(g.geocode_intersection("Broadway", "59th Street", M), (40.767696, -73.981679))
    # these are interpolations
    assert_close(g.geocode_intersection("Broadway", "24th Street", M), (40.7422035, -73.989151))
    assert_close(g.geocode_intersection("Broadway", "124th St", M), (40.8140625, -73.959421))
    # this isn't great, but probably not too far off the intended location.
    assert_close(g.geocode_intersection("Broadway", "127th St.", M), (40.816311, -73.957802))


def test_geocode_st_nicholas():
    # This one is tricky because it's a rare case where "St." does not mean "Street".
    g = Grid()
    assert_close(
        g.geocode_intersection("St. Nicholas Ave", "145th Street (West)", M), (40.82404, -73.944764)
    )


def test_geocode_above_125():
    g = Grid()
    assert_close(g.geocode_intersection("7th Avenue", "134th Street", M), (40.8146691, -73.94419))


def test_parse_ave():
    assert grid.parse_ave("Broadway") == "Broadway"
    assert grid.parse_ave("Fifth Avenue") == "5"
    assert grid.parse_ave("Avenue A") == "A"
    assert grid.parse_ave("Central Park West") == "Central Park West"
    assert grid.parse_ave("Riverside Park") == "Riverside Drive"


def test_extract_street_num():
    assert grid.extract_street_num("123rd Street") == 123
    assert grid.extract_street_num("12th St.") == 12
    assert grid.extract_street_num("31st St.") == 31
    assert grid.extract_street_num("5th Avenue") is None
    assert grid.extract_street_num("Fifty-fourth Street") == 54
    assert grid.extract_street_num("One Hundred and Forty-first Street") == 141
    assert grid.extract_street_num("Seventh Avenue") is None
    assert grid.extract_street_num("One hundred and forty-sixth Street") == 146
    assert grid.extract_street_num("Seventy-third to Seventy-fourth Street") == 73


def test_normalize_street():
    assert grid.normalize_street("Fifth Avenue") == "5th Avenue"
    assert grid.normalize_street("Twelfth Street (East)") == "12th Street (East)"
    assert grid.normalize_street("second avenue") == "2nd avenue"
    assert (
        grid.normalize_street("One hundred and forty-sixth Street")
        == "One hundred and forty-sixth Street"
    )
    assert (
        grid.normalize_street("One hundred and twelfth Street") == "One hundred and twelfth Street"
    )
    assert grid.normalize_street("6th St") == "6th Street"
    assert grid.normalize_street("N. 7th St.") == "North 7th Street"
    assert grid.normalize_street("String St") == "String Street"
    assert grid.normalize_street("Frederick Douglass Blvd") == "Frederick Douglass Boulevard"
    assert grid.normalize_street("Central Park W") == "Central Park West"
    assert grid.normalize_street("Maiden Ln") == "Maiden Lane"
    assert grid.normalize_street("St Nicholas") == "Saint Nicholas"
    assert grid.normalize_street("10th St E") == "10th Street East"
    assert grid.normalize_street_for_osm("Avenue E") == "Avenue E"
    # TODO: just fix this bug?
    assert grid.normalize_street("Avenue E") == "Avenue East"
    assert (
        grid.normalize_street_for_osm("Dr. Martin Luther King Jr. Expressway")
        == "Dr. Martin Luther King Jr. Expressway"
    )


# 10th Street and Sixth Avenue, Brooklyn
def test_brooklyn_intersections():
    g = Grid()
    assert_close(
        g.geocode_intersection("10th Street", "6th Avenue", "Brooklyn"), (40.667437, -73.984438)
    )


def test_strip_dir():
    assert grid.strip_dir("10th Street (East)") == "10th Street"
    assert grid.strip_dir("10th Street (West)") == "10th Street"
    assert grid.strip_dir("West 59th Street") == "59th Street"
    assert grid.strip_dir("North 4th Street") == "4th Street"
    assert grid.strip_dir("West Street") == "West Street"
    assert grid.strip_dir("South Street") == "South Street"
    assert grid.strip_dir("East End Avenue") == "East End Avenue"
    assert grid.strip_dir("West End Avenue") == "West End Avenue"
    assert grid.strip_dir("Central Park West") == "Central Park West"


def test_preserved_streets():
    g = Grid()
    assert_close(
        g.geocode_intersection("East 76th Street", "East End Avenue", "Manhattan"),
        (40.782401, -73.982596),
        # (40.770415, -73.948064),
    )
    # 40.782401
