from oldnyc.ocr import cleaner

samples = [
    # 0
    """120-130 Baxter Street, west side, at, adjoining, and south of
the S.W. corner of Hester Street. The view also shows 200-202 Hester
Street, at and adjoining the S.W. corner of Baxter Street.
About 1925.
MAY BE REPRODUCED.
""",
    # 1
    """The 440 Club was a popular downstairs watering hole for
local office inhabitants. So named - 4 East 40th. After
losing 1ease it became a restaurant which failed within a
short time. Bldg will be demolished to sske way for new
(proposed) hoae of Ihe Republic National Bank.
Earl Christian, photographer (NnPL)
Aug.1979
""",
    # 2
    """1. Panorama from hill above Swan St., Stapleton, S.I.
Sept. 7, 1939
P.L. Sperr, photographer
ce. Sane as above
3. Same as above
""",
    # 3
    """(1)
Eleventh Avenue at northeast cornsr of 57th Street,
and showing buildings on north west side of Avenue.
May 20, 1927.
(2)
Eleventh Avenue northeast corner 57th Street, Gas
Sfation in plain site.
P.L.Speer.
NO REPRODU IONS.  September 19, 1933.
""",
    # 4
    """308 E. 37th Street, south side, east of Second Avenue.
The easterly half of St. Gabriel's Roman Catholic Church as
viewed northwaro from the alter rail. TCo the lett appears the
organ loft and the large stained window that is over the entrance.
.January 11, 1939
Somach Yhoto Service
New York City Tunnel Authority
CPDlr LLND IEERA1IvE
""",
    # 5
    """New Dock Street, west side, north of Water Street, show-
ing W. P. S. workmen erecting a new storehouse for the New York
City Department of Purchase under the Brooklyn Bridge.
June 17, 1936
Works Progress Administration
Project 65-97-68
CREDIT LINE IMPERATIVE
""",
    # 6
    """Coney Island: The beach and boardwalk on a hot August after-
noon, looking east.
1939
Alexaneer Alland
Ap7-:  Wg ~E 33~4
""",
    # 7
    """(1) Bryant Park, center and west side, towards 42nd Street, giving a rear view of the Federal Hell repilos, on which demolition is beginning. April 8, 1933. P. L. Sperr. NO REPHODUCTIONS.

(2) The same view, but closer to 42nd Street, showing the Park being remodelled under the regime of Commissioner Robert Moses, New York's first city-wide Commissioner of Parks. March 15, 1934. P. L. Sperr. NO REPHODUCTIONS.

(3) The same, seen from the south side, and showing the Park after completion of the work. The flower beds are planted with ivy. The large corner building, at Sixth Avenue and 42nd Street, is the department store of Stern Brothers. July 6, 1935. P. L. Sperr. NO REPHODUCTIONS.
""",
    # 8: 731107b
    """Harlem River bridges--Willis Avenue Bridge: The Willis A Avenue (Bronx) Bridge over the Harlem River. It is also known as the 1st Avenue (Manhattan) Bridge.

        View 2 shows the 1st Avenue approach to the bridge.

View 1: George L. Balgue                          August, 1930


View 2: P. L. Sperr                                   August, 1936
""",
    # 9
    """54 and 56 (right to left) Irving Place, adjoining and north of the N. E. corner of E. 17th Street, showing two 3 story former private dwellings. That, with the bay window is now occupied by the Cooperative Cafeteria, an enterprise long associated with the wife of Norman Thomas, the Socialist.
June 1938
George D. Chinn
NEG #3039
""",
    # 10
    """Sixth Avenue, North from West 4th Street, after the removal of the "L".

January I7th, 1939

P. L. Sperr.""",
    # 11
    """379 Madison Street, north side and north west corner of Jackson Street, showing P.S. 12.

Board of Education, N.Y.C.
CREDIT LINE IMPERATIVE. 1920.
NEG: 2870""",
    # 12
    """(1) Hoyt Street, east side, from Schermerhorn to State Streets, Also seen is 311-313 1/2 State Street, at the N.E. corner of Hoyt Street. May 25, 1929. P. L. Sperr.  (2) The same, showing the house which was built about 1874 by the Clark family whose estate comprise surrounding area. April 7, 1932. P. L. Sperr.  (3) The same, from a different angle. April 7, 1932. P. L. Sperr.""",
    # 13
    "Dime Savings Bank of Brooklyn\nmain office\n\nF. S. LINCOLN\nPhotographer\n114 EAST 32nd STREET\nNEW YORK CITY\n123 P.V.\n\nIF PUBLISHED, CREDIT\nIS TO BE GIVEN TO\nF. S. LINCOLN",
    # 14 - 721373b
    "COPYRIGHT BY\nF. S. LINCOLN\nPhotographer\n114 EAST 32nd STREET\nNEW YORK CITY\nTHS PRINT IS SOLD FOR REFERENCE ONLY. REPRODUCTION IS NOT AL OWE D IN ANY FORM WITHOUT WRITTEN P RMISS ON FROM F. S. LINCOLN\n955P4\nConstance Spry\n",
]


def test_remove_warning():
    assert "MAY BE REPRODUCED" in samples[0]
    assert "MAY BE REPRODUCED" not in cleaner.remove_warnings(samples[0])

    assert "CPDlr LLND IEERA1IvE" in samples[4]
    assert "CPDlr LLND IEERA1IvE" not in cleaner.remove_warnings(samples[4])

    assert "CREDIT LINE IMPERATIVE" in samples[11]
    assert "1920" in samples[11]
    assert "1920" in cleaner.remove_warnings(samples[11])
    assert "CREDIT LINE IMPERATIVE" not in cleaner.remove_warnings(samples[11])


def test_merge_lines():
    txt = cleaner.remove_warnings(samples[0])
    assert """120-130 Baxter Street, west side, at, adjoining, and south of the S.W. corner of Hester Street. The view also shows 200-202 Hester Street, at and adjoining the S.W. corner of Baxter Street.
About 1925.
""" == cleaner.merge_lines(txt)

    txt = cleaner.remove_warnings(samples[1])
    assert """The 440 Club was a popular downstairs watering hole for local office inhabitants. So named - 4 East 40th. After losing 1ease it became a restaurant which failed within a short time. Bldg will be demolished to sske way for new (proposed) hoae of Ihe Republic National Bank.
Earl Christian, photographer (NnPL)
Aug.1979
""" == cleaner.merge_lines(txt)

    txt = cleaner.remove_warnings(samples[2])
    assert txt == cleaner.merge_lines(txt)

    # XXX: it would be better if the "Sfation" line were merged up.
    txt = cleaner.remove_warnings(samples[3])
    assert """(1)
Eleventh Avenue at northeast cornsr of 57th Street, and showing buildings on north west side of Avenue.
May 20, 1927.
(2)
Eleventh Avenue northeast corner 57th Street, Gas
Sfation in plain site.
P.L.Speer.
NO REPRODU IONS.  September 19, 1933.
""" == cleaner.merge_lines(txt)

    txt = cleaner.remove_warnings(samples[4])
    assert """308 E. 37th Street, south side, east of Second Avenue. The easterly half of St. Gabriel's Roman Catholic Church as viewed northwaro from the alter rail. TCo the lett appears the organ loft and the large stained window that is over the entrance.
.January 11, 1939
Somach Yhoto Service
New York City Tunnel Authority
""" == cleaner.merge_lines(txt)

    # This one has a hyphenated phrase which gets joined
    txt = cleaner.remove_warnings(samples[5])
    assert """New Dock Street, west side, north of Water Street, showing W. P. S. workmen erecting a new storehouse for the New York City Department of Purchase under the Brooklyn Bridge.
June 17, 1936
Works Progress Administration
Project 65-97-68
""" == cleaner.merge_lines(txt)

    # This one has a hyphen followed by a short line.
    txt = cleaner.remove_warnings(samples[6])
    assert """Coney Island: The beach and boardwalk on a hot August afternoon, looking east.
1939
Alexaneer Alland
Ap7-:  Wg ~E 33~4
""" == cleaner.merge_lines(txt)

    # This has no trailing newline
    txt = "Hello\nThere"
    assert "Hello\nThere" == cleaner.clean(txt)


def test_partial_warning():
    txt = cleaner.remove_warnings(samples[7])
    assert txt == (
        """(1) Bryant Park, center and west side, towards 42nd Street, giving a rear view of the Federal Hell repilos, on which demolition is beginning. April 8, 1933. P. L. Sperr.

(2) The same view, but closer to 42nd Street, showing the Park being remodelled under the regime of Commissioner Robert Moses, New York's first city-wide Commissioner of Parks. March 15, 1934. P. L. Sperr.

(3) The same, seen from the south side, and showing the Park after completion of the work. The flower beds are planted with ivy. The large corner building, at Sixth Avenue and 42nd Street, is the department store of Stern Brothers. July 6, 1935. P. L. Sperr.
"""
    )


def test_remove_negative():
    txt = cleaner.remove_neg(samples[9])
    assert txt == (
        """54 and 56 (right to left) Irving Place, adjoining and north of the N. E. corner of E. 17th Street, showing two 3 story former private dwellings. That, with the bay window is now occupied by the Cooperative Cafeteria, an enterprise long associated with the wife of Norman Thomas, the Socialist.
June 1938
George D. Chinn
"""
    )


def test_is_negative():
    texts = [
        "NEG #3039",
        "Negative No. 400",
        "Neg. #1767",
        "NEG # 3457",
        "Neg. # 2246",
        "Negative # 3956",
        "Neg. # 2689",
        "Neg. # 1458",
        "Neg. # 2231",
        "Neg. # 1106",
        "Neg. #724",
        "NEG# 3507",
        "Neg. No. A-1074",
        "Neg # 717",
        "Negative No. 375.",
        "NEG. # 4546",
        "Neg. H 829.",
        "Slide #109",
        "Neg. no. 45",
        "Neg. # -1407",
        "Neg #601 A",
        "Neg # 601 C",
        "NEG:#3553",
        "NEG; 2822",
        "Neg. # 1786A",
        # "D4 Neg. # 4041",
        "Neg. No. 98a",
        # "Neg. Photostat #",
        # "Negative Photostat # 1192",
        "NEG # 3613A",
        # "D2 - NEG # 3268"
        # "D2- NEGH # 3268"
        # "D3 NEGH # 3277"
        # "D3 NEG # 3277"
        "Neg # A.1378",
        "Neg. No. A_513",
        "Neg # 603B 4x5 neg",
        "Neg # 686 8x10 neg",
        # "756 D2 VIEW 1 - NEG. #3332"
        # "756 D3 " 2. NEG # 3333"
        # "756 D4 " 3 NEG # 3334"
        "Neg. No. A_349",
        "Neg. No. A 535",
        "Neg. No. A. 535",
        "Neg. photograph available in G. Neg. No. 1",
    ]
    for text in texts:
        assert cleaner.is_negative(text), text

    negatives = [
        "1931.",
        "Neg. B-12 - B-15 Bridges - Highbridge",  # 730832b
        "Neg. A-449  Sunnyside Yards.",  # 727293b, 727296b
    ]
    for text in negatives:
        assert not cleaner.is_negative(text), text


def test_fix_i17th():
    assert cleaner.swap_chars("April 19,I941") == "April 19,1941"
    assert cleaner.swap_chars("June IIth, 1913.") == "June 11th, 1913."
    # II2th to II4th Streets,
    txt = cleaner.clean(samples[10])
    assert txt == (
        """Sixth Avenue, North from West 4th Street, after the removal of the "L".

January 17th, 1939

P. L. Sperr."""
    )


def test_split_interior_whitespace():
    assert (
        cleaner.split_interior_whitespace(samples[8])
        == """Harlem River bridges--Willis Avenue Bridge: The Willis A Avenue (Bronx) Bridge over the Harlem River. It is also known as the 1st Avenue (Manhattan) Bridge.

View 2 shows the 1st Avenue approach to the bridge.

View 1: George L. Balgue
August, 1930


View 2: P. L. Sperr
August, 1936
"""
    )

    assert (
        cleaner.split_interior_whitespace(samples[12])
        == """(1) Hoyt Street, east side, from Schermerhorn to State Streets, Also seen is 311-313 1/2 State Street, at the N.E. corner of Hoyt Street. May 25, 1929. P. L. Sperr.

(2) The same, showing the house which was built about 1874 by the Clark family whose estate comprise surrounding area. April 7, 1932. P. L. Sperr.

(3) The same, from a different angle. April 7, 1932. P. L. Sperr."""
    )


def test_remove_stamps():
    assert cleaner.remove_stamps(samples[13]) == "Dime Savings Bank of Brooklyn\nmain office\n"
    assert cleaner.remove_stamps(samples[14]) == "Constance Spry\n"
