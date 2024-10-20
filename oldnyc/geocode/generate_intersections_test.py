from oldnyc.geocode.generate_intersections import make_avenue_str, make_street_str


def test_make_street_str():
    assert "East 1st street" == make_street_str(1, 1)
    assert "East 2nd street" == make_street_str(2, 1)
    assert "East 3rd street" == make_street_str(3, 1)
    assert "East 4th street" == make_street_str(4, 1)
    assert "East 9th street" == make_street_str(9, 1)
    assert "East 11th street" == make_street_str(11, 1)
    assert "East 12th street" == make_street_str(12, 1)
    assert "East 13th street" == make_street_str(13, 1)
    assert "East 21st street" == make_street_str(21, 1)
    assert "East 22nd street" == make_street_str(22, 1)
    assert "East 100th street" == make_street_str(100, 1)
    assert "West 101st street" == make_street_str(101, 8)
    assert "West 102nd street" == make_street_str(102, 8)
    assert "East 121st street" == make_street_str(121, 1)


def test_make_avenue_str():
    assert "Avenue A" == make_avenue_str(0)
    assert "Avenue D" == make_avenue_str(-3)
    assert "1st Avenue" == make_avenue_str(1)
    assert "2nd Avenue" == make_avenue_str(2)
    assert "3rd Avenue" == make_avenue_str(3)

    assert "Park Avenue South" == make_avenue_str(4, 17)
    assert "Park Avenue South" == make_avenue_str(4, 32)
    assert "Park Avenue" == make_avenue_str(4, 59)
