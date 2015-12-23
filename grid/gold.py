#!/usr/bin/env python
'''Generate golden data for Manhattan intersections.

'''
import geocoder
import random


# See http://stackoverflow.com/a/20007730/388951
def make_ordinal(n):
    return '%d%s' % (n, 'tsnrhtdd'[(n/10%10!=1)*(n%10<4)*n%10::4])


def make_street_str(street):
    '''1 -> 1st Street'''
    return make_ordinal(street) + ' street'


def make_avenue_str(avenue, street=0):
    '''1 --> 1st Avenue, -1 --> Avenue B'''
    if avenue <= 0:
        return 'Avenue ' + ['A', 'B', 'C', 'D'][-avenue]
    elif avenue == 4:
        if 17 <= street <= 32:
            return 'Park Avenue South'
        elif street > 32:
            return 'Park Avenue'
    elif avenue == 6 and street >= 110:
        return 'Malcolm X Blvd'
    elif avenue == 7 and street >= 110:
        return 'Adam Clayton Powell Jr Blvd'
    elif avenue == 8 and 59 <= street <= 110:
        return 'Central Park West'
    elif avenue == 8 and street > 110:
        return 'Frederick Douglass Blvd'
    elif avenue == 10 and street >= 59:
        return 'Amsterdam Avenue'
    elif avenue == 11 and street >= 59:
        return 'West End Avenue'
    else:
        return make_ordinal(avenue) + ' Avenue'


'''
10th Avenue --> Amsterdam Ave above 59th street
11th Avenue --> West End Ave above 59th street
 8th Avenue --> Central Park West from 59th to 110th
 8th Avenue --> Frederick Douglass Blvd above 110th
 7th Avenue --> Adam Clayton Powell Jr Blvd above 110th
 6th Avenue --> Malcolm X Blvd above 110th
 4th Avenue --> Park Avenue S from 17th to 32nd street
 4th Avenue --> Park Avenue above 32nd street
'''


def locate(avenue, street):
    '''Avenue & Street are numbers. Returns (lat, lon).
    Avenue A is -1.
    '''
    street_str = make_street_str(street)
    avenue_str = make_avenue_str(avenue, street)
    response = g.Locate('%s and %s, Manhattan, NY' % (street_str, avenue_str))

    r = response['results'][0]
    if r['types'] != ['intersection']: return None
    if r.get('partial_match'): return None  # may be inaccurate

    loc = r['geometry']['location']
    lat_lon = loc['lat'], loc['lng']

    return lat_lon

if __name__ == '__main__':
    g = geocoder.Geocoder(True, 1)  # use network, 1s wait time.

    crosses = []
    # for street in range(14, 125):
    #     for ave in range(-3, 13):
    #         crosses.append((ave, street))
    for street in range(1, 14):
        for ave in range(-3, 7):
            crosses.append((ave, street))
    # random.shuffle(crosses)

    for i, (ave, street) in enumerate(crosses):
        lat, lon = locate(ave, street) or ('', '')
        print '%d\t%d\t%s\t%s' % (street, ave, lat, lon)
        # print '%d / %d --> %s / %s --> %s' % (
        #         1 + i, len(crosses),
        #         make_street_str(street), make_avenue_str(ave), lat_lon)
