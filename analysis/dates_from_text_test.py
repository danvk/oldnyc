from analysis.dates_from_text import get_dates_from_text


text_701590f = """Pelham Bay Park - Orchard Beach: Shown, in a set of three views, are
the newly erected bath houses built by the Works Progress Administration.
Orchard Beach came into existence when part of Pelham Bay, separating Hunters Island
from Rodmans Neck, was filled in. The three views were taken the same day.
January 25, 1938
W.P.A. photo  Views 1,2 and 3
Five Boroughs Project
"""

text_701593f = """(1)
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
"""

text_726768f = """Grand Ave. (partially seen, trolley thereon in the right background),
south side, east of 59th to 60th Streets. Shown in the background are the homes of Cord
Meyer Sr. and Jr. in 1891. These homes were demolished
in 1934. This is a set of three views.
March 1923.
Eugene L. Armbruster Collection.
"""

text_705487f = """285 Livingston Street, north side, between Hanover Place and Nevins
Street. (This house was not in existence in 1929).
1922.
Eugene L. Armbruster Collection.
"""
text_728074f = """Sutphin Boulevard, east side, between Linden Boulevard and 114th Road,
showing the J. O'Donnell house belonging to him and members of his family fron 1860 to 1896.
He was the owner of the Jamaica Standard, a local newspaper. View No. 2 shows the house
on August Court (now non-existent), as seen from Linden Boulevard (right foreground), viewed
southward.
April 1925.
Views 1 and 2.
Eugene L. Armbruster Collection.
"""

text_709781f = """#560 Seventh Avenue at the North West corner of West 40th Street.
November 8th,1914.
Wurts Brothers,
"""

text_723901f = """Wall Street at the North East corner of Nassau Street,
showing the Roger Williams Crusaders group laying a wreath before the statue of
George Washington, (statue by J.Q.A. Ward), in front of the Old Sub Treasury Building.
Views 2&3 are the same. About 1930.
"""

text_715761f = """(1) 553-557 West 169th Street, north side, west of Audubon Avenue.
1932.

J. Clarence Davies Collection, Museum of the City of New York.
Negative No. 55

(2) The same as No. 1.
November 5, 1934.
P.L. Sperr.

(3) The same, showing only Nos. 555 and 557.
October 12, 1934.
P. L. Sperr.
"""

text_717267f = """537-541 & 543 Broadway, west side, north of Spring Street.
Prior to 1919.

Gift of E.  M. Jenks
NEG # 3082
"""

text_704696f = """
Greene Avenue, north side, at Clermont Avenue,
View 1 is east and shows St. Johns (R.C.)
Chapel. View 2 is west across Clermont Avenue.

P. L. Sperr  September 20, 1941"""

text_726086f = """
Astoria Boulevard, at the S.W. corner of 49th Street--the old Bowery Hay Road--
showing the Queens County Hotel, built in 1873 by Mrs. Christian Scheurer
and established as a hotel in 1875, with her son Wm. H. Scheurer as manager.
The edge of St. Michaels Cemetery is on the extreme left.

View 1: April, 1923
View 2: April, 1925
Views 3,4: June 3, 1927

Views 1,2: Eugene L. Armbruster Collection

Views 3,4: P. L. Sperr
"""

text_725053f = """
19th Avenue, north side, between 45th and 47th Streets,
showing, in the distance, the white Cassabeer House, known in 1933 as
Steinway Lodge. A large shingled barn can be seen on the right.
The views are north from 19th Avenue, toward
the East River, which the house overlooks.
Eugene L. Armbruster Collection  Views 1,2: 1923
MAY BE REPRODUCED  View 3: 1925
"""

text_708323f = """
Thirty, Fifth Ave., the new apartment building at Fifth ave. and W. Tenth Street,
which has been financed by the American Bond & Mortgage Company, and
which will be open for occupancy next week.

Addition to Washington Square growing apartment colony.

15 story Building at South West corner of 5th  Ave. and 10th Street.

Neg # 529
c. 1923
"""

text_726224f = """
Brnadwav, weat afde, betweew Coorona Avenue and St. dames Avenue,
ahowing in the foreground in the three views the d.A. Taawrence
house of 1873. The small house beyond it belonged to D. I. Rapelye.
All houses seen in these views were either moved
or demolished by October 1930.
1oe2 E.
Views 1 and 2
Views 3:May 1923.
Eugene L. Armbruster Collection
May be reproduced.

"""

text_726214f = """
Broadway, north side, between Britton Avenue and Pettit Place,
showing an old frame dwelling. It belonged to one
Williamson in 1891.
P. L. Sperr  View 1: April 25, 1936
NO REPRODUCTIiNS  Views 2,3: November 5, 1936
"""

text_708722f = """
Fifth Avenue, west side, at 41st Street, showing the New York
Public Library and one of its watchful lions.
Winter 1939
Alexander Alland

"""

text_711019f = """
E. 10th Street, north side, east from (No. 375, a three story building
at the left and demolished in the Fall of 1938) a point between Avenue\'s
B and C and towards the latter. This series of 4 photos was taken to
show slum area, fire and health hazards. Additional material will be
found under subject heading
"Social Conditions."

Fall, 1938
Views : 1-4

Gift of Committee on Housing
Charity Organization Society
"""

text_716310f = """
Amsterdam Avenue, north from West 124th Street. View 2 is limited to
a northward perspective on the east side of this Avenue. No. 3 shows
the blockfront extending from La Salle Street on the left to 124th
Street on the right. Note the garage building in all three of these
photos.

No. 1: July, 1928
No. 2: Spring, 1940
No. 3: Sept., 1928

No's 1 & 3
George L. Balgue, photo

No. 2
P.L. Sperr

"""

text_702545f = """
East 14th Street, west side, between Aves. E and Y. This is a
2-story frame building.
July 9. 1936.
P. L. Sperr.

"""


def test_get_full_date():
    assert get_dates_from_text(text_701590f) == ["1938-01-25"]
    assert get_dates_from_text(text_701593f) == ["1928-05-29", "1928-05-29", "1928-05-29"]
    assert get_dates_from_text(text_704696f) == ["1941-09-20"]
    assert get_dates_from_text(text_726214f) == ["1936-04-25", "1936-11-05"]
    assert get_dates_from_text(text_702545f) == ["1936-07-09"]


def test_prioritize_lone_date():
    assert get_dates_from_text(text_726768f) == ["1923-03"]  # not 1891 or 1934
    assert get_dates_from_text(text_705487f) == ["1922"]  # not 1929
    assert get_dates_from_text(text_728074f) == ["1925-04"]  # not 1860 or 1896
    assert get_dates_from_text("September 1937") == ["1937-09"]
    assert get_dates_from_text("Sept. 1937") == ["1937-09"]
    assert get_dates_from_text("Sep. 1937") == ["1937-09"]


def test_date_no_space():
    assert get_dates_from_text(text_709781f) == ["1914-11-08"]


def test_about_prior_circa():
    assert get_dates_from_text(text_723901f) == ["1930"]
    assert get_dates_from_text(text_717267f) == ["1919"]  # could be range: ['1800', '1919']
    assert get_dates_from_text(text_708323f) == ["1923"]


def test_multiple_dates():
    assert get_dates_from_text(text_715761f) == ["1932", "1934-11-05", "1934-10-12"]


def test_views():
    assert get_dates_from_text(text_725053f) == ["1923", "1925"]
    assert get_dates_from_text(text_726224f) == ["1923-05"]


def test_seasons():
    assert get_dates_from_text(text_708722f) == ["1939"]
    assert get_dates_from_text(text_711019f) == ["1938"]
    assert get_dates_from_text(text_716310f) == ["1928-07", "1928-09", "1940"]
