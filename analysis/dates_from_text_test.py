from analysis.dates_from_text import get_dates_from_text


text_701590f = '''Pelham Bay Park - Orchard Beach: Shown, in a set of three views, are
the newly erected bath houses built by the Works Progress Administration.
Orchard Beach came into existence when part of Pelham Bay, separating Hunters Island
from Rodmans Neck, was filled in. The three views were taken the same day.
January 25, 1938
W.P.A. photo  Views 1,2 and 3
Five Boroughs Project
'''

text_701593f = '''(1)
Pelham Bay Park: A view of the Pine Island station of the Life Saving Service of the
City of New York on the shore of Eastchester Bay.
May 29, 1928.
P. L. Sperr.
(2)
The same, another view.
May 29, 1928.
P. L. Sperr.
(3)
An additional view from a different angle.
May 29, 1928.
P. L. Sperr.
'''

text_726768f = '''Grand Ave. (partially seen, trolley thereon in the right background),
south side, east of 59th to 60th Streets. Shown in the background are the homes of Cord
Meyer Sr. and Jr. in 1891. These homes were demolished
in 1934. This is a set of three views.
March 1923.
Eugene L. Armbruster Collection.
'''

text_705487f = '''285 Livingston Street, north side, between Hanover Place and Nevins
Street. (This house was not in existence in 1929).
1922.
Eugene L. Armbruster Collection.
'''
text_728074f = '''Sutphin Boulevard, east side, between Linden Boulevard and 114th Road,
showing the J. O'Donnell house belonging to him and members of his family fron 1860 to 1896.
He was the owner of the Jamaica Standard, a local newspaper. View No. 2 shows the house
on August Court (now non-existent), as seen from Linden Boulevard (right foreground), viewed
southward.
April 1925.
Views 1 and 2.
Eugene L. Armbruster Collection.
'''

text_709781f = '''#560 Seventh Avenue at the North West corner of West 40th Street.
November 8th,1914.
Wurts Brothers,
'''

text_723901f = '''Wall Street at the North East corner of Nassau Street,
showing the Roger Williams Crusaders group laying a wreath before the statue of
George Washington, (statue by J.Q.A. Ward), in front of the Old Sub Treasury Building.
Views 2&3 are the same. About 1930.
'''

text_715761f = '''(1) 553-557 West 169th Street, north side, west of Audubon Avenue.
1932.

J. Clarence Davies Collection, Museum of the City of New York.
Negative No. 55

(2) The same as No. 1.
November 5, 1934.
P.L. Sperr.

(3) The same, showing only Nos. 555 and 557.
October 12, 1934.
P. L. Sperr.
'''

text_717267f = '''537-541 & 543 Broadway, west side, north of Spring Street.
Prior to 1919.

Gift of E.  M. Jenks
NEG # 3082
'''

text_704696f = '''
Greene Avenue, north side, at Clermont Avenue, View 1 is east and shows St. Johns (R.C.)
Chapel. View 2 is west across Clermont Avenue.

P. L. Sperr  September 20, 1941'''

def test_get_full_date():
    assert get_dates_from_text(text_701590f) == ['1938-01-25']
    assert get_dates_from_text(text_701593f) == ['1928-05-29', '1928-05-29','1928-05-29']
    assert get_dates_from_text(text_704696f) == ['1941-09-20']

def test_prioritize_lone_date():
    assert get_dates_from_text(text_726768f) == ['March 1923']  # not 1891 or 1934
    assert get_dates_from_text(text_705487f) == ['1922']  # not 1929
    assert get_dates_from_text(text_728074f) == ['April 1925']  # not 1860 or 1896


def test_date_no_space():
    assert get_dates_from_text(text_709781f) == ['1914-11-08']


def test_about_prior():
    assert get_dates_from_text(text_723901f) == ['1930']
    assert get_dates_from_text(text_717267f) == ['1919']  # could be range: ['1800', '1919']


def test_multiple_dates():
    assert get_dates_from_text(text_715761f) == ['1932', '1934-11-05', '1934-10-12']
