from dates import extract_years

def test_extract_dates():
    assert extract_years('1927') == ['1927']
    assert extract_years('ca. 1927') == ['1927']
    assert extract_years('1927?') == ['1927']
    assert extract_years('1932; 1933') == ['1932', '1933']
    assert extract_years('Jan. 8, 1927') == ['1927']
    assert extract_years('n.d.') == ['']
    assert extract_years('[1925-1931]') == ['1925', '1931']
