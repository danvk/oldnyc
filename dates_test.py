from nose.tools import *

from dates import extract_years

def test_extract_dates():
    eq_(['1927'], extract_years('1927'))
    eq_(['1927'], extract_years('ca. 1927'))
    eq_(['1927'], extract_years('1927?'))
    eq_(['1932', '1933'], extract_years('1932; 1933'))
    eq_(['1927'], extract_years('Jan. 8, 1927'))
    eq_([''], extract_years('n.d.'))
    eq_(['1925', '1931'], extract_years('[1925-1931]'))
