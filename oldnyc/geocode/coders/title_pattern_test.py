from oldnyc.geocode.coders.title_pattern import (
    TitleAddressCoder,
    TitleCrossCoder,
    clean_and_strip_title,
    extract_braced_clauses,
    rewrite_directional_street,
)
from oldnyc.geocode.geocode_types import AddressLocation, IntersectionLocation
from oldnyc.item import blank_item


def test_title_pattern():
    tp = TitleCrossCoder()
    title = "Manhattan: 10th Street (East) - Broadway"
    item = blank_item()
    item.title = title
    assert tp.code_record(item) == IntersectionLocation(
        source=title, str1="10th Street (East)", str2="Broadway", boro="Manhattan"
    )

    title = "Richmond: 3rd Street - New Dorp Lane"
    item.title = title
    assert tp.code_record(item) == IntersectionLocation(
        source=title, str1="3rd Street", str2="New Dorp Lane", boro="Staten Island"
    )

    title = "Manhattan: 6th Avenue - 37th and 38th Streets (West)"
    item.title = title
    assert tp.code_record(item) is None

    # 725017f
    item.title = "Queens: 12th Street - North 27th Avenue."
    assert tp.code_record(item) == IntersectionLocation(
        source="Queens: 12th Street - North 27th Avenue.",
        str1="12th Street",
        str2="North 27th Avenue",
        boro="Queens",
    )


def test_alt_title():
    tp = TitleCrossCoder()
    item = blank_item()

    item.title = "Feast of Our Lady of Mount Carmel."
    item.alt_title = ["Manhattan: 1st Avenue - 112th Street ."]
    assert tp.code_record(item) == IntersectionLocation(
        source=item.alt_title[0], str1="112th Street", str2="1st Avenue", boro="Manhattan"
    )

    # 730343f
    item.title = "General view - Cedar Street - South."
    item.alt_title = [
        "Manhattan: Cedar Street - Pearl Street ; 1 Cedar Street ; Municipal Building."
    ]
    assert tp.code_record(item) == IntersectionLocation(
        source="Manhattan: Cedar Street - Pearl Street",
        str1="Cedar Street",
        str2="Pearl Street",
        boro="Manhattan",
    )


def test_braces():
    tp = TitleCrossCoder()
    title = "Manhattan: 5th Avenue - [53rd Street]"
    item = blank_item()
    item.title = title
    assert tp.code_record(item) == IntersectionLocation(
        source="Manhattan: 5th Avenue - 53rd Street",
        str1="53rd Street",
        str2="5th Avenue",
        boro="Manhattan",
    )


def test_between():
    tp = TitleCrossCoder()
    item = blank_item()
    # 708379f
    item.title = "Manhattan: 5th Avenue - [Between 23rd and 24th Streets]"
    assert tp.code_record(item) == IntersectionLocation(
        source="Manhattan: 5th Avenue - Between 23rd and 24th Streets",
        str1="23rd Street",
        str2="5th Avenue",
        boro="Manhattan",
    )

    # 731177f
    item.title = "Manhattan: 5th Avenue - Between 25th and 26th Streets."
    assert tp.code_record(item) == IntersectionLocation(
        source="Manhattan: 5th Avenue - Between 25th and 26th Streets.",
        str1="25th Street",
        str2="5th Avenue",
        boro="Manhattan",
    )

    # 711722f
    item.title = "Manhattan: [London Terrace - Typical one room apartment (interior).]"
    item.alt_title = ["Manhattan: 23rd Street (West) - Between 9th and 10th Avenues."]
    assert tp.code_record(item) == IntersectionLocation(
        source="Manhattan: 23rd Street (West) - Between 9th and 10th Avenues.",
        str1="23rd Street (West)",
        str2="9th Avenue",
        boro="Manhattan",
    )


def test_number_prefix():
    # 1558017
    tp = TitleCrossCoder()
    item = blank_item()
    item.subject.geographic = ["Manhattan (New York, N.Y.)"]
    item.title = "1065 Sixth Avenue - West 40th Street."
    assert tp.code_record(item) == IntersectionLocation(
        source="Manhattan: 1065 Sixth Avenue - West 40th Street.",
        str1="Sixth Avenue",
        str2="West 40th Street",
        boro="Manhattan",
    )

    # 1558253
    # "11 West 54th Street - Fifth Avenue, Manhattan, NY"
    item.title = "11 West 54th Street - Fifth Avenue."
    assert tp.code_record(item) == IntersectionLocation(
        source="Manhattan: 11 West 54th Street - Fifth Avenue.",
        str1="Fifth Avenue",
        str2="West 54th Street",
        boro="Manhattan",
    )

    # 1557791
    item.title = "Brooklyn - 100 Henry Street - Clark Street"
    assert tp.code_record(item) == IntersectionLocation(
        source="Brooklyn - 100 Henry Street - Clark Street",
        str1="Clark Street",
        str2="Henry Street",
        boro="Brooklyn",
    )


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
    tp = TitleCrossCoder()
    item = blank_item()
    # 708014f
    item.title = "Manhattan: 3rd Avenue - west side - between 16th and 17th Street."
    assert (
        clean_and_strip_title(item.title)
    ) == "Manhattan: 3rd Avenue - between 16th and 17th Street."
    assert tp.code_record(item) == IntersectionLocation(
        source="Manhattan: 3rd Avenue - between 16th and 17th Street.",
        str1="16th Street",
        str2="3rd Avenue",
        boro="Manhattan",
    )


def test_at():
    tp = TitleCrossCoder()
    item = blank_item()
    # 485798
    item.title = "3rd Avenue at 97th Street and , East side to North, Manhattan"
    assert (clean_and_strip_title(item.title)) == "3rd Avenue at 97th Street, Manhattan"
    assert tp.code_record(item) == IntersectionLocation(
        source="3rd Avenue at 97th Street, Manhattan",
        str1="3rd Avenue",
        str2="97th Street",
        boro="Manhattan",
    )


def test_and_name():
    tp = TitleCrossCoder()
    item = blank_item()
    # 725938f
    item.title = "Queens: 160th Street - Grand Central Parkway"
    assert tp.code_record(item) == IntersectionLocation(
        source="Queens: 160th Street - Grand Central Parkway",
        str1="160th Street",
        str2="Grand Central Parkway",
        boro="Queens",
    )


def test_boro_dash():
    tp = TitleCrossCoder()
    item = blank_item()
    # 1557751
    item.title = "Bronx - Findlay Avenue - East 167th Street"
    assert tp.code_record(item) == IntersectionLocation(
        source="Bronx - Findlay Avenue - East 167th Street",
        str1="East 167th Street",
        str2="Findlay Avenue",
        boro="Bronx",
    )


def test_general_view():
    # 730413f
    tp = TitleCrossCoder()
    item = blank_item()
    item.title = "General view - [Manhattan - Park Avenue - 34th Street (Northeast)]."
    assert extract_braced_clauses(item.title) == [
        "Manhattan - Park Avenue - 34th Street (Northeast)"
    ]
    # TODO: could strip out "(Northeast)"
    assert tp.code_record(item) == IntersectionLocation(
        source="Manhattan - Park Avenue - 34th Street (Northeast)",
        str1="34th Street (Northeast)",
        str2="Park Avenue",
        boro="Manhattan",
    )


def test_space_colon():
    tp = TitleCrossCoder()
    item = blank_item()
    # 709296f
    item.title = "Manhattan : 6th Avenue - 3rd Street (West)."
    assert tp.code_record(item) == IntersectionLocation(
        source="Manhattan: 6th Avenue - 3rd Street (West).",
        str1="3rd Street (West)",
        str2="6th Avenue",
        boro="Manhattan",
    )


def test_add_dots():
    "Brooklyn: Surf Ave. - 10th St. W."


def test_decoy_address():
    tp = TitleCrossCoder()
    item = blank_item()
    # 1507919
    item.title = "42nd Street (East) #122 - Lexington Avenue, southwest corner"
    item.source = "blah / Manhattan"
    assert tp.code_record(item) == IntersectionLocation(
        source="Manhattan: 42nd Street (East) #122 - Lexington Avenue, ",
        str1="42nd Street (East)",
        str2="Lexington Avenue",
        boro="Manhattan",
    )


def test_address_coder():
    coder = TitleAddressCoder()
    item = blank_item()
    # 1508895
    item.title = "Fifth Avenue #1067 - 87th Street, east side - looking west"
    assert coder.code_record(item) == AddressLocation(
        source="Fifth Avenue #1067", num="1067", street="Fifth Avenue", boro="Manhattan"
    )

    # 1507775
    item.title = "38th Street (West) #247-49"
    assert coder.code_record(item) == AddressLocation(
        source="38th Street (West) #247", num="247", street="W 38th Street", boro="Manhattan"
    )

    # 1508975
    item.title = "Bowery Street #4-8"
    assert coder.code_record(item) == AddressLocation(
        source="Bowery Street #4", num="4", street="Bowery Street", boro="Manhattan"
    )

    # 1507871
    item.title = "34th Street (West) #167"
    assert coder.code_record(item) == AddressLocation(
        source="34th Street (West) #167", num="167", street="W 34th Street", boro="Manhattan"
    )

    # 711033f
    item.title = "Manhattan: 10th Street (West) - [Greenwich and Washington Streets]"
    item.alt_title = ["271 West 10th Street ; Empire Brewery."]
    assert coder.code_record(item) == AddressLocation(
        source="271 West 10th Street", num="271", street="West 10th Street", boro="Manhattan"
    )


def test_rewrite_directional_street():
    assert rewrite_directional_street("34th Street (West)") == "W 34th Street"
    assert rewrite_directional_street("5th Avenue") == "5th Avenue"
    assert rewrite_directional_street("51st Street (East)") == "E 51st Street"
    assert rewrite_directional_street("8th Street (South)") == "S 8th Street"


# More to look at:

# 1509723
"Fifth Avenue - 18th Street, northwest corner -"
# 1509729
"Fifth Avenue - 23rd Street looking north"
# 715990f
"Manhattan: Amsterdam Avenue - Cathedral Parkway - 113th Street"

# 720847f
"Manhattan: Lenox Avenue - 120th Street: Left photo: View 1, Lenox Avenue, e. s., n. fr. 120th Street. View 2, Lenox Avenue, e. s., n. fr. 120th Street."
# 417427
"The Alimar, Northwest corner West End Avenue and 105th Street."
# 1507697
"Tenth Avenue - 25th Street - 26th Street, west side"

# 1516945
"1873 2nd Ave. between 96th and 97th St."
# 709447f
"Manhattan: 6th Avenue - 37th and 38th Streets (West)"

# Currently matched by Milstein:

# 465559
"Cromwell Apartments, northwest corner Broadway and 137th Street; Plan of first floor; Plan of upper floors."
# 733357f
"Manhattan: Bleecker Street ; 383 Bleecker Street."
# 465538
"Audubon Park Apartments, southeast corner Broadway and 156th Street; Plan of first floor; Plan of upper floors."


# 730530f
"Queens] - Airports - La Guardia Field."
