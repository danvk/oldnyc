from nose.tools import *

from ocr import cleaner

samples = [
# 0
'''120-130 Baxter Street, west side, at, adjoining, and south of
the S.W. corner of Hester Street. The view also shows 200-202 Hester
Street, at and adjoining the S.W. corner of Baxter Street.
About 1925.
MAY BE REPRODUCED.
''',

# 1
'''The 440 Club was a popular downstairs watering hole for
local office inhabitants. So named - 4 East 40th. After
losing 1ease it became a restaurant which failed within a
short time. Bldg will be demolished to sske way for new
(proposed) hoae of Ihe Republic National Bank.
Earl Christian, photographer (NnPL)
Aug.1979
''',

# 2
'''1. Panorama from hill above Swan St., Stapleton, S.I.
Sept. 7, 1939
P.L. Sperr, photographer
ce. Sane as above
3. Same as above
''',

# 3
'''(1)
Eleventh Avenue at northeast cornsr of 57th Street,
and showing buildings on north west side of Avenue.
May 20, 1927.
(2)
Eleventh Avenue northeast corner 57th Street, Gas
Sfation in plain site.
P.L.Speer.
NO REPRODU IONS.  September 19, 1933.
''',

# 4
'''308 E. 37th Street, south side, east of Second Avenue.
The easterly half of St. Gabriel's Roman Catholic Church as
viewed northwaro from the alter rail. TCo the lett appears the
organ loft and the large stained window that is over the entrance.
.January 11, 1939
Somach Yhoto Service
New York City Tunnel Authority
CPDlr LLND IEERA1IvE
''',

# 5
'''New Dock Street, west side, north of Water Street, show-
ing W. P. S. workmen erecting a new storehouse for the New York
City Department of Purchase under the Brooklyn Bridge.
June 17, 1936
Works Progress Administration
Project 65-97-68
CREDIT LINE IMPERATIVE
''',

# 6
'''Coney Island: The beach and boardwalk on a hot August after-
noon, looking east.
1939
Alexaneer Alland
Ap7-:  Wg ~E 33~4
''',

# 7
'''(1) Bryant Park, center and west side, towards 42nd Street, giving a rear view of the Federal Hell repilos, on which demolition is beginning. April 8, 1933. P. L. Sperr. NO REPHODUCTIONS.

(2) The same view, but closer to 42nd Street, showing the Park being remodelled under the regime of Commissioner Robert Moses, New York's first city-wide Commissioner of Parks. March 15, 1934. P. L. Sperr. NO REPHODUCTIONS.

(3) The same, seen from the south side, and showing the Park after completion of the work. The flower beds are planted with ivy. The large corner building, at Sixth Avenue and 42nd Street, is the department store of Stern Brothers. July 6, 1935. P. L. Sperr. NO REPHODUCTIONS.
'''
]


def test_remove_warning():
    assert 'MAY BE REPRODUCED' in samples[0]
    assert 'MAY BE REPRODUCED' not in cleaner.remove_warnings(samples[0])

    assert 'CPDlr LLND IEERA1IvE' in samples[4]
    assert 'CPDlr LLND IEERA1IvE' not in cleaner.remove_warnings(samples[4])


def test_merge_lines():
    txt = cleaner.remove_warnings(samples[0])
    eq_('''120-130 Baxter Street, west side, at, adjoining, and south of the S.W. corner of Hester Street. The view also shows 200-202 Hester Street, at and adjoining the S.W. corner of Baxter Street.
About 1925.
''',
    cleaner.merge_lines(txt))

    txt = cleaner.remove_warnings(samples[1])
    eq_('''The 440 Club was a popular downstairs watering hole for local office inhabitants. So named - 4 East 40th. After losing 1ease it became a restaurant which failed within a short time. Bldg will be demolished to sske way for new (proposed) hoae of Ihe Republic National Bank.
Earl Christian, photographer (NnPL)
Aug.1979
''',
    cleaner.merge_lines(txt))

    txt = cleaner.remove_warnings(samples[2])
    eq_(txt, cleaner.merge_lines(txt))

    # XXX: it would be better if the "Sfation" line were merged up.
    txt = cleaner.remove_warnings(samples[3])
    eq_('''(1)
Eleventh Avenue at northeast cornsr of 57th Street, and showing buildings on north west side of Avenue.
May 20, 1927.
(2)
Eleventh Avenue northeast corner 57th Street, Gas
Sfation in plain site.
P.L.Speer.
NO REPRODU IONS.  September 19, 1933.
''',
    cleaner.merge_lines(txt))

    txt = cleaner.remove_warnings(samples[4])
    eq_('''308 E. 37th Street, south side, east of Second Avenue. The easterly half of St. Gabriel's Roman Catholic Church as viewed northwaro from the alter rail. TCo the lett appears the organ loft and the large stained window that is over the entrance.
.January 11, 1939
Somach Yhoto Service
New York City Tunnel Authority
''',
    cleaner.merge_lines(txt))

    # This one has a hyphenated phrase which gets joined
    txt = cleaner.remove_warnings(samples[5])
    eq_('''New Dock Street, west side, north of Water Street, showing W. P. S. workmen erecting a new storehouse for the New York City Department of Purchase under the Brooklyn Bridge.
June 17, 1936
Works Progress Administration
Project 65-97-68
''',
    cleaner.merge_lines(txt))

    # This one has a hyphen followed by a short line.
    txt = cleaner.remove_warnings(samples[6])
    eq_('''Coney Island: The beach and boardwalk on a hot August afternoon, looking east.
1939
Alexaneer Alland
Ap7-:  Wg ~E 33~4
''',
    cleaner.merge_lines(txt))

    # This has no trailing newline
    txt = 'Hello\nThere'
    eq_('Hello\nThere', cleaner.clean(txt))


def test_partial_warning():
    txt = cleaner.remove_warnings(samples[7])
    assert txt == ('''(1) Bryant Park, center and west side, towards 42nd Street, giving a rear view of the Federal Hell repilos, on which demolition is beginning. April 8, 1933. P. L. Sperr.

(2) The same view, but closer to 42nd Street, showing the Park being remodelled under the regime of Commissioner Robert Moses, New York's first city-wide Commissioner of Parks. March 15, 1934. P. L. Sperr.

(3) The same, seen from the south side, and showing the Park after completion of the work. The flower beds are planted with ivy. The large corner building, at Sixth Avenue and 42nd Street, is the department store of Stern Brothers. July 6, 1935. P. L. Sperr.
''')
