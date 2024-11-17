from oldnyc.geocode.osm.generate_intersections import make_avenue_str


def test_make_avenue_str():
    assert "Avenue A" == make_avenue_str(0)
    assert "Avenue D" == make_avenue_str(-3)
    assert "1st Avenue" == make_avenue_str(1)
    assert "2nd Avenue" == make_avenue_str(2)
    assert "3rd Avenue" == make_avenue_str(3)

    assert "Park Avenue South" == make_avenue_str(4, 17)
    assert "Park Avenue South" == make_avenue_str(4, 32)
    assert "Park Avenue" == make_avenue_str(4, 59)
