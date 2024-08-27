#!/usr/bin/env python

import csv
import json
import re
import sys
from collections import defaultdict

import numpy as np

by_avenue = defaultdict(lambda: {})
by_street = defaultdict(lambda: {})

for row in csv.DictReader(open('grid/intersections.csv')):
    if not row['Lat']: continue  # not all intersections exist.
    avenue = int(row['Avenue'])
    street = int(row['Street'])
    lat = float(row['Lat'])
    lon = float(row['Lon'])
    if avenue <= 0:
        avenue = ['A', 'B', 'C', 'D'][-avenue]
    else:
        avenue = str(avenue)
    by_avenue[avenue][street] = (lat, lon)
    by_street[street][avenue] = (lat, lon)


AVE_TO_NUM = {'A': 0, 'B': -1, 'C': -2, 'D': -3}
def ave_to_num(ave):
    if ave in AVE_TO_NUM:
        return AVE_TO_NUM[ave]
    else:
        return int(ave)


def correl(xs_list, ys_list):
    xs = np.array(xs_list, dtype=float)
    ys = np.array(ys_list, dtype=float)
    meanx = xs.mean()
    meany = ys.mean()
    stdx = xs.std()
    stdy = ys.std()
    return ((xs * ys).mean() - meanx * meany) / (stdx * stdy)


def extract_lat_lons(num_to_lls):
    '''Returns (xs, lats, lons) as parallel lists.'''
    lats = sorted([(ave_to_num(x), num_to_lls[x][0]) for x in num_to_lls.keys()])
    lons = sorted([(ave_to_num(x), num_to_lls[x][1]) for x in num_to_lls.keys()])
    ns = [x[0] for x in lats]
    lats = [x[1] for x in lats]
    lons = [x[1] for x in lons]
    return ns, lats, lons


def correl_lat_lons(num_to_lls):
    '''Measure how straight a street is.

    Given a dict mapping street/ave # --> (lat, lon), returns min(r^2).
    '''
    xs, lats, lons = extract_lat_lons(num_to_lls)
    r_lat = correl(xs, lats)
    r_lon = correl(xs, lons)
    return min(r_lat * r_lat, r_lon * r_lon)


def get_line(num_to_lls):
    '''Get the line (lat=a*lon+b) for a street or avenue.

    Returns (b, a), i.e. (intercept, slope)
    '''
    ns, lats, lons = extract_lat_lons(num_to_lls)
    xs = np.zeros((len(lons), 2))
    xs[:,0] = 1
    xs[:,1] = lons
    ys = np.array(lats)
    return np.linalg.lstsq(xs, ys)[0]


def extrapolate_intersection(avenue, street):
    street_to_lls = by_avenue[avenue]
    ave_to_lls = by_street[street]

    if (correl_lat_lons(street_to_lls) < 0.99 or
        correl_lat_lons(ave_to_lls) < 0.99):
        return None

    b_ave, a_ave = get_line(street_to_lls)
    b_str, a_str = get_line(ave_to_lls)

    lon = (b_ave - b_str) / (a_str - a_ave)
    lat = b_ave + lon * a_ave

    return lat, lon


def may_extrapolate(avenue, street):
    '''Is this a valid intersection to extrapolate?'''
    ave_num = ave_to_num(avenue)
    str_num = int(street)

    # This cuts out the West Village and 4th Avenue south of 14th Street.
    # Streets are crooked there.
    # Valid intersections in those areas should be exact.
    if str_num <= 14 and ave_num > 2:
        return False
    # Avenues B, C and D should not extend above 23rd. They'd be underwater!
    elif str_num >= 23 and ave_num < 0:
        return False
    return True


num_exact = 0
num_unclaimed = 0
num_extrapolated = 0

def code(avenue, street):
    '''Find the location of a current or historical intersection.

    `avenue` and `street` are strings, e.g. 'A' and '15'.
    Returns (lat, lon) or None.
    '''
    global num_exact, num_unclaimed, num_extrapolated

    crosses = by_avenue.get(avenue)
    if not crosses:
        sys.stderr.write('No cross for %s\n' % avenue)
        num_unclaimed += 1
        return None

    # First look for an exact match.
    exact = crosses.get(int(street))
    if exact:
        num_exact += 1
        return (exact[0], exact[1])

    # Otherwise, find where the street and avenue would logically intersect one
    # another if they continued as straight lines.
    street_crosses = by_street.get(int(street))
    if not street_crosses:
        sys.stderr.write('Street %s is unknown\n' % street)
        num_unclaimed += 1
        return None

    if not may_extrapolate(avenue, street):
        sys.stderr.write('Rejecting extrapolation for %s, %s\n' % (avenue, street))
        return None

    num_extrapolated += 1
    return extrapolate_intersection(avenue, int(street))


if __name__ == '__main__':
    print('Avenues:')
    for ave in sorted(by_avenue.keys()):
        r2 = correl_lat_lons(by_avenue[ave])
        if r2 < 0.99:
            print('  %3s: %s' % (ave, r2))

    print('Streets:')
    for street in sorted(by_street.keys()):
        r2 = correl_lat_lons(by_street[street])
        if r2 < 0.99:
            print('  %3s: %s' % (street, r2))
