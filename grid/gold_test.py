from grid import gold


def test_make_street_str():
    assert "1st street" == gold.make_street_str(1)
    assert "2nd street" == gold.make_street_str(2)
    assert "3rd street" == gold.make_street_str(3)
    assert "4th street" == gold.make_street_str(4)
    assert "9th street" == gold.make_street_str(9)
    assert "11th street" == gold.make_street_str(11)
    assert "12th street" == gold.make_street_str(12)
    assert "13th street" == gold.make_street_str(13)
    assert "21st street" == gold.make_street_str(21)
    assert "22nd street" == gold.make_street_str(22)
    assert "100th street" == gold.make_street_str(100)
    assert "101st street" == gold.make_street_str(101)
    assert "102nd street" == gold.make_street_str(102)
    assert "121st street" == gold.make_street_str(121)


def test_make_avenue_str():
    assert "Avenue A" == gold.make_avenue_str(0)
    assert "Avenue D" == gold.make_avenue_str(-3)
    assert "1st Avenue" == gold.make_avenue_str(1)
    assert "2nd Avenue" == gold.make_avenue_str(2)
    assert "3rd Avenue" == gold.make_avenue_str(3)

    assert "Park Avenue South" == gold.make_avenue_str(4, 17)
    assert "Park Avenue South" == gold.make_avenue_str(4, 32)
    assert "Park Avenue" == gold.make_avenue_str(4, 59)
