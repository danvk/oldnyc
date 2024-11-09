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

    item.title = "Feast of Our Lady of Mount Carmel."
    item.alt_title = ["Manhattan: 1st Avenue - 112th Street ."]
    assert tp.codeRecord(item) == {
        "type": "intersection",
        "source": item.alt_title[0],
        "address": "112th Street and 1st Avenue, Manhattan, NY",
        "data": ("112th Street", "1st Avenue", "Manhattan"),
    }

    # 730343f
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


def test_braces():
    tp = TitlePatternCoder()
    title = "Manhattan: 5th Avenue - [53rd Street]"
    item = blank_item()
    item.title = title
    assert tp.codeRecord(item) == {
        "type": "intersection",
        "source": "Manhattan: 5th Avenue - 53rd Street",
        "address": "53rd Street and 5th Avenue, Manhattan, NY",
        "data": ("53rd Street", "5th Avenue", "Manhattan"),
    }


def test_between():
    tp = TitlePatternCoder()
    item = blank_item()
    # 708379f
    item.title = "Manhattan: 5th Avenue - [Between 23rd and 24th Streets]"
    assert tp.codeRecord(item) == {
        "type": "intersection",
        "source": "Manhattan: 5th Avenue - Between 23rd and 24th Streets",
        "address": "23rd Street and 5th Avenue, Manhattan, NY",
        "data": ("23rd Street", "5th Avenue", "Manhattan"),
    }

    # 731177f
    item.title = "Manhattan: 5th Avenue - Between 25th and 26th Streets."
    assert tp.codeRecord(item) == {
        "type": "intersection",
        "source": "Manhattan: 5th Avenue - Between 25th and 26th Streets.",
        "address": "25th Street and 5th Avenue, Manhattan, NY",
        "data": ("25th Street", "5th Avenue", "Manhattan"),
    }

    # 711722f
    item.title = "Manhattan: [London Terrace - Typical one room apartment (interior).]"
    item.alt_title = ["Manhattan: 23rd Street (West) - Between 9th and 10th Avenues."]
    assert tp.codeRecord(item) == {
        "type": "intersection",
        "source": "Manhattan: 23rd Street (West) - Between 9th and 10th Avenues.",
        "address": "23rd Street (West) and 9th Avenue, Manhattan, NY",
        "data": ("23rd Street (West)", "9th Avenue", "Manhattan"),
    }
