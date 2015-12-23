#!/usr/bin/env python
'''Given an old and new data.json file, find the differences.

Reports added & dropped photos, plus IDs which have moved a significant distance.
'''

from collections import defaultdict
from math import radians, cos, sin, asin, sqrt
import json
import sys

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    km = 6367 * c
    return km


def dist(latlon1, latlon2):
    '''Returns the distance in short Manhattan blocks.'''
    lat1, lon1 = latlon1
    lat2, lon2 = latlon2
    return haversine(lon1, lat1, lon2, lat2) / 0.0804672


def load_lat_lons(path):
    '''Returns a photo_id --> (lat, lon) map for a data.json file.'''
    return {x['photo_id']: (x['location']['lat'], x['location']['lon'])
            for x in json.load(open(path))['photos']}


def find_big_movers(old_lls, new_lls):
    for photo_id in new_ids.intersection(old_ids):
        if dist(old_lls[photo_id], new_lls[photo_id]) >= 0.5:
            yield photo_id


if __name__ == '__main__':
    old_path, new_path = sys.argv[1:]
    old_lls = load_lat_lons(old_path)
    new_lls = load_lat_lons(new_path)

    old_ids = set(old_lls.keys())
    new_ids = set(new_lls.keys())

    print 'New photos: %d' % (len(new_ids.difference(old_ids)))
    print 'Dropped photos: %d' % (len(old_ids.difference(new_ids)))

    int_ids = new_ids.intersection(old_ids)
    print 'Photos in both: %d' % len(int_ids)

    movers = list(find_big_movers(old_lls, new_lls))
    num_movers = len(movers)
    print '# with big movements: %d' % num_movers

    movements = defaultdict(list)
    for photo_id in movers:
        ll1 = old_lls[photo_id]
        ll2 = new_lls[photo_id]
        d = dist(ll1, ll2)
        movements[(d, ll1[0], ll1[1], ll2[0], ll2[1])].append(photo_id)

    for (d, lat1, lon1, lat2, lon2), photo_ids in movements.iteritems():
        print '%f\t%f\t%f\t%f\t%f\t%s' % (d, lat1, lon1, lat2, lon2, ', '.join(photo_ids))
