from oldnyc.geocode.geogpt.extract_gpt_geocodes import is_suspicious_address


def test_is_suspicious_address():
    assert is_suspicious_address(1, "1st Street")
    assert is_suspicious_address(155, "155th Street (West)")
    assert not is_suspicious_address(3, "East 83rd Street")
