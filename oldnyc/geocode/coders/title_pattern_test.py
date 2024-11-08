from oldnyc.geocode.coders.title_pattern import TitlePatternCoder
from oldnyc.item import blank_item


def test_title_pattern():
    tp = TitlePatternCoder()
    title = "Manhattan: 10th Street (East) - Broadway"
    item = blank_item()
    item.title = title
    assert tp.codeRecord(item) == {
        "type": "intersection",
        "source": title,
        "address": "10th Street (East) & Broadway, Manhattan, NY",
    }

    title = "Richmond: 3rd Street - New Dorp Lane"
    item.title = title
    assert tp.codeRecord(item) == {
        "type": "intersection",
        "source": title,
        "address": "3rd Street & New Dorp Lane, Staten Island, NY",
    }

    title = "Manhattan: 6th Avenue - 37th and 38th Streets (West)"
    item.title = title
    assert tp.codeRecord(item) is None
