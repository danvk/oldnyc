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
        "address": "10th Street (East) and Broadway, Manhattan, NY",
        "data": ("10th Street (East)", "Broadway", "Manhattan"),
    }

    title = "Richmond: 3rd Street - New Dorp Lane"
    item.title = title
    assert tp.codeRecord(item) == {
        "type": "intersection",
        "source": title,
        "address": "3rd Street and New Dorp Lane, Staten Island, NY",
        "data": ("3rd Street", "New Dorp Lane", "Staten Island"),
    }

    title = "Manhattan: 6th Avenue - 37th and 38th Streets (West)"
    item.title = title
    assert tp.codeRecord(item) is None


def test_alt_title():
    tp = TitlePatternCoder()
    item = blank_item()
    item.title = "General view - Cedar Street - South."
    item.alt_title = [
        "Manhattan: Cedar Street - Pearl Street ; 1 Cedar Street ; Municipal Building."
    ]
    assert tp.codeRecord(item) is None

    # TODO: split on ';' and try each one
    # == {
    #     "type": "intersection",
    #     "source": item.alt_title[0],
    #     "address": "Cedar Street and Pearl Street, Manhattan, NY",
    #     "data": ("Cedar Street", "Pearl Street", "Manhattan"),
    # }
