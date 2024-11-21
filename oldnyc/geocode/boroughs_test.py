from oldnyc.geocode.boroughs import is_in_manhattan, point_to_borough

pt_in_bk = (40.6909958, -73.9892384)


def test_is_in_manhattan():
    assert not is_in_manhattan(*pt_in_bk)
    assert point_to_borough(*pt_in_bk) == "Brooklyn"


def test_point_to_borough():
    assert point_to_borough(40.689453822582465, -74.04557985575643) == "Manhattan"  # Liberty Island
    assert point_to_borough(40.7315696474075, -73.9956358298509) == "Manhattan"
    assert point_to_borough(40.79062042127515, -73.92361565896147) == "Manhattan"

    assert point_to_borough(40.847343414326474, -73.7876283011962) == "Bronx"

    assert point_to_borough(40.73606521672497, -73.83142380616343) == "Queens"
    assert point_to_borough(40.644884704983696, -73.78335396650323) == "Queens"

    assert point_to_borough(40.66163446918125, -73.96894600124809) == "Brooklyn"

    assert point_to_borough(40.58257183949479, -74.13562578973973) == "Staten Island"

    assert point_to_borough(40.741658981099704, -74.03124110640505) is None


# 278630910, 10001064063, 6224367558, 6933321234, 10001064062, 10001064061, 4209410680
# 42492210, 10761116389, 6224367557, 278630910
