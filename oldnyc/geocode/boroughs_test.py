from oldnyc.geocode.boroughs import is_in_manhattan, point_to_borough

pt_in_bk = (40.6909958, -73.9892384)


def test_is_in_manhattan():
    assert not is_in_manhattan(*pt_in_bk)
    assert point_to_borough(*pt_in_bk) == "Brooklyn"


# 278630910, 10001064063, 6224367558, 6933321234, 10001064062, 10001064061, 4209410680
# 42492210, 10761116389, 6224367557, 278630910
