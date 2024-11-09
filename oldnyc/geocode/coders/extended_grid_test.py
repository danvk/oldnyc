from oldnyc.geocode.coders.extended_grid import parse_street_ave


def test_parse_street_ave():
    assert parse_street_ave("122nd St", "1st Ave") == ("1", "122")
    assert parse_street_ave("1st Ave", "122nd St") == ("1", "122")
    assert parse_street_ave("18th Street", "Avenue A") == ("A", "18")
    assert parse_street_ave("18th Street (West)", "4th Avenue") == ("4", "18")
