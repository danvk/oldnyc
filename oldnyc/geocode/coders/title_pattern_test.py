from oldnyc.geocode.coders.title_pattern import (
    TitlePatternCoder,
    clean_and_strip_title,
    extract_braced_clauses,
)
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
    assert tp.codeRecord(item) == {
        "type": "intersection",
        "source": "Manhattan: Cedar Street - Pearl Street",
        "address": "Cedar Street and Pearl Street, Manhattan, NY",
        "data": ("Cedar Street", "Pearl Street", "Manhattan"),
    }


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


def test_number_prefix():
    # 1558017
    tp = TitlePatternCoder()
    item = blank_item()
    item.subject.geographic = ["Manhattan (New York, N.Y.)"]
    item.title = "1065 Sixth Avenue - West 40th Street."
    assert tp.codeRecord(item) == {
        "type": "intersection",
        "source": "Manhattan: 1065 Sixth Avenue - West 40th Street.",
        "address": "Sixth Avenue and West 40th Street, Manhattan, NY",
        "data": ("Sixth Avenue", "West 40th Street", "Manhattan"),
    }

    # 1558253
    # "11 West 54th Street - Fifth Avenue, Manhattan, NY"
    item.title = "11 West 54th Street - Fifth Avenue."
    assert tp.codeRecord(item) == {
        "type": "intersection",
        "source": "Manhattan: 11 West 54th Street - Fifth Avenue.",
        "address": "Fifth Avenue and West 54th Street, Manhattan, NY",
        "data": ("Fifth Avenue", "West 54th Street", "Manhattan"),
    }

    # 1557791
    item.title = "Brooklyn - 100 Henry Street - Clark Street"
    assert tp.codeRecord(item) == {
        "type": "intersection",
        "source": "Brooklyn - 100 Henry Street - Clark Street",
        "address": "Clark Street and Henry Street, Brooklyn, NY",
        "data": ("Clark Street", "Henry Street", "Brooklyn"),
    }


def test_strip_trivia():
    assert (
        clean_and_strip_title("Manhattan: 3rd Avenue - west side - between 16th and 17th Street.")
        == "Manhattan: 3rd Avenue - between 16th and 17th Street."
    )
    assert (
        clean_and_strip_title("3rd Avenue at 97th Street and , East side to North, Manhattan")
        == "3rd Avenue at 97th Street, Manhattan"
    )
    assert (
        clean_and_strip_title("Manhattan: 3rd Avenue - west corner - 13th Street.")
        == "Manhattan: 3rd Avenue - 13th Street."
    )


def test_pattern_with_trivia():
    tp = TitlePatternCoder()
    item = blank_item()
    # 708014f
    item.title = "Manhattan: 3rd Avenue - west side - between 16th and 17th Street."
    assert (
        clean_and_strip_title(item.title)
    ) == "Manhattan: 3rd Avenue - between 16th and 17th Street."
    assert tp.codeRecord(item) == {
        "type": "intersection",
        "source": "Manhattan: 3rd Avenue - between 16th and 17th Street.",
        "address": "16th Street and 3rd Avenue, Manhattan, NY",
        "data": ("16th Street", "3rd Avenue", "Manhattan"),
    }


def test_at():
    tp = TitlePatternCoder()
    item = blank_item()
    # 485798
    item.title = "3rd Avenue at 97th Street and , East side to North, Manhattan"
    assert (clean_and_strip_title(item.title)) == "3rd Avenue at 97th Street, Manhattan"
    assert tp.codeRecord(item) == {
        "type": "intersection",
        "source": "3rd Avenue at 97th Street, Manhattan",
        "address": "3rd Avenue and 97th Street, Manhattan, NY",
        "data": ("3rd Avenue", "97th Street", "Manhattan"),
    }


def test_and_name():
    tp = TitlePatternCoder()
    item = blank_item()
    # 725938f
    item.title = "Queens: 160th Street - Grand Central Parkway"
    assert tp.codeRecord(item) == {
        "type": "intersection",
        "source": "Queens: 160th Street - Grand Central Parkway",
        "address": "160th Street and Grand Central Parkway, Queens, NY",
        "data": ("160th Street", "Grand Central Parkway", "Queens"),
    }


def test_boro_dash():
    tp = TitlePatternCoder()
    item = blank_item()
    # 1557751
    item.title = "Bronx - Findlay Avenue - East 167th Street"
    assert tp.codeRecord(item) == {
        "type": "intersection",
        "source": "Bronx - Findlay Avenue - East 167th Street",
        "address": "East 167th Street and Findlay Avenue, Bronx, NY",
        "data": ("East 167th Street", "Findlay Avenue", "Bronx"),
    }


def test_general_view():
    # 730413f
    tp = TitlePatternCoder()
    item = blank_item()
    item.title = "General view - [Manhattan - Park Avenue - 34th Street (Northeast)]."
    assert extract_braced_clauses(item.title) == [
        "Manhattan - Park Avenue - 34th Street (Northeast)"
    ]
    # TODO: could strip out "(Northeast)"
    assert tp.codeRecord(item) == {
        "type": "intersection",
        "source": "Manhattan - Park Avenue - 34th Street (Northeast)",
        "address": "34th Street (Northeast) and Park Avenue, Manhattan, NY",
        "data": ("34th Street (Northeast)", "Park Avenue", "Manhattan"),
    }


def test_space_colon():
    tp = TitlePatternCoder()
    item = blank_item()
    # 709296f
    item.title = "Manhattan : 6th Avenue - 3rd Street (West)."
    assert tp.codeRecord(item) == {
        "type": "intersection",
        "source": "Manhattan: 6th Avenue - 3rd Street (West).",
        "address": "3rd Street (West) and 6th Avenue, Manhattan, NY",
        "data": ("3rd Street (West)", "6th Avenue", "Manhattan"),
    }


# More to look at:

# 1509723
"Fifth Avenue - 18th Street, northwest corner -"
# 1509729
"Fifth Avenue - 23rd Street looking north"
# 715990f
"Manhattan: Amsterdam Avenue - Cathedral Parkway - 113th Street"
# 1508895
"Fifth Avenue #1067 - 87th Street, east side - looking west"
# 720847f
"Manhattan: Lenox Avenue - 120th Street: Left photo: View 1, Lenox Avenue, e. s., n. fr. 120th Street. View 2, Lenox Avenue, e. s., n. fr. 120th Street."
# 417427
"The Alimar, Northwest corner West End Avenue and 105th Street."
# 1507697
"Tenth Avenue - 25th Street - 26th Street, west side"
# 1508127
"Park Avenue #301 - 48th Street - 50th Street"
# 1516945
"1873 2nd Ave. between 96th and 97th St."

# Currently matched by Milstein:

# 465559
"Cromwell Apartments, northwest corner Broadway and 137th Street; Plan of first floor; Plan of upper floors."
# 733357f
"Manhattan: Bleecker Street ; 383 Bleecker Street."
# 465538
"Audubon Park Apartments, southeast corner Broadway and 156th Street; Plan of first floor; Plan of upper floors."


# 730530f
"Queens] - Airports - La Guardia Field."
