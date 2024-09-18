#!/usr/bin/env python
"""Various output formats for generate-geocodes.py."""

import json
from coders.types import Location
import record
import sys
from collections import defaultdict

from json import encoder
encoder.FLOAT_REPR = lambda o: format(o, '.6f')

# http://stackoverflow.com/questions/1342000/how-to-replace-non-ascii-characters-in-string
def removeNonAscii(s): return "".join(i for i in s if ord(i)<128)


def loadBlacklist():
    # unused for now
    return set()


LocatedRecord = tuple[record.Record, str, Location]


def _generateJson(located_recs: list[LocatedRecord], lat_lon_map: dict[str, str]):
    out = {}
    # "lat,lon" -> list of photo_ids
    ll_to_id = defaultdict(list)

    codes = []
    claimed_in_map = {}

    # load a blacklist as a side input
    blacklist = loadBlacklist()

    for r, coder, location_data in located_recs:
        if not location_data: continue
        photo_id = r['id']

        lat = location_data['lat']
        lon = location_data['lon']
        ll_str = '%.6f,%.6f' % (lat, lon)
        if lat_lon_map and ll_str in lat_lon_map:
            claimed_in_map[ll_str] = True
            ll_str = lat_lon_map[ll_str]
        if ll_str in blacklist: continue
        ll_to_id[ll_str].append(r)

    #print len(claimed_in_map)
    #print len(lat_lon_map)
    #assert len(claimed_in_map) == len(lat_lon_map)

    no_date = 0
    points = 0
    photos = 0
    for lat_lon, recs in ll_to_id.items():
        rec_dates = [(r, record.get_date_range(r)) for r in recs]
        # XXX the "if" filter here probably doesn't do anything
        sorted_recs = sorted([rdr for rdr in rec_dates
                              if rdr[1] and rdr[1][1]],
                             key=lambda rdr: rdr[1][1])
        no_date += (len(recs) - len(sorted_recs))

        out_recs = []
        for r, date_range in sorted_recs:
            assert date_range
            assert date_range[0]
            assert date_range[1]
            out_recs.append([
                date_range[0].year, date_range[1].year, r['id']])

        if out_recs:
            points += 1
            photos += len(out_recs)
            out[lat_lon] = out_recs

    sys.stderr.write('Dropped w/ no date: %d\n' % no_date)
    sys.stderr.write('Unique lat/longs: %d\n' % points)
    sys.stderr.write('Total photographs: %d\n' % photos)

    return out


def printJson(located_recs: list[LocatedRecord], lat_lon_map: dict[str, str]):
    data = _generateJson(located_recs, lat_lon_map)

    print("var lat_lons = ")
    print(json.dumps(data, sort_keys=True))


def printJsonNoYears(located_recs: list[LocatedRecord], lat_lon_map: dict[str, str]):
    data = _generateJson(located_recs, lat_lon_map)
    for k, v in data.items():
            data[k] = [x[2] for x in v]    # drop both year elements.

    print("var lat_lons = ")
    print(json.dumps(data, sort_keys=True))


def printRecordsJson(located_recs: list[LocatedRecord]):
    recs = []
    for r, coder, location_data in located_recs:
        rec = {
            'id': r['id'],
            'folder': removeNonAscii(r['location'].replace('Folder: ', '')),
            'date': record.clean_date(r['date']),
            'title': removeNonAscii(record.clean_title(r['title'])),
            'description': removeNonAscii(r.get('description', '')),
            'url': r['preferred_url'],
            'extracted': {
                'date_range': [ None, None ]
            }
        }
        if r.get('note'):
            # Are there any of these?
            rec['note'] = r['note']

        start, end = record.get_date_range(r)
        rec['extracted']['date_range'][0] = '%04d-%02d-%02d' % (
                start.year, start.month, start.day)
        rec['extracted']['date_range'][1] = '%04d-%02d-%02d' % (
                end.year, end.month, end.day)

        if coder:
            rec['extracted']['latlon'] = (location_data['lat'], location_data['lon'])
            rec['extracted']['located_str'] = removeNonAscii(location_data['address'])
            rec['extracted']['technique'] = coder

        try:
            x = json.dumps(rec)
        except Exception as e:
            sys.stderr.write('%s\n' % rec)
            raise e

        recs.append(rec)
    # Net effect of this is to round lat/lngs to 6 decimals in the JSON, to match the
    # web site and the behavior of old version of this code.
    # https://stackoverflow.com/a/29066406/388951
    print(
        json.dumps(
            json.loads(json.dumps(recs), parse_float=lambda x: round(float(x), 6)),
            indent=2,
            sort_keys=True,
        )
    )


def printRecordsText(located_recs: list[LocatedRecord]):
    for r, coder, location_data in located_recs:
        date = record.clean_date(r['date'])
        title = record.clean_title(r['title'])
        folder = r['location']
        if folder: folder = record.clean_folder(folder)

        if location_data:
            lat = location_data['lat']
            lon = location_data['lon']
            loc = (str((lat, lon)) or '') + '\t' + location_data['address']
        else:
            loc = 'n/a\tn/a'

        print('\t'.join([r['id'], date, folder, title, r['preferred_url'], coder or 'failed', loc]))


def printIdLocation(located_recs: list[LocatedRecord]):
    for r, coder, location_data in located_recs:
        if location_data:
            lat = location_data["lat"]
            lon = location_data["lon"]
            loc = (str((lat, lon)) or "") + "\t" + location_data["address"]
        else:
            loc = "n/a\tn/a"

        print("\t".join([r["id"], coder or "failed", loc]))


def printLocations(located_recs: list[LocatedRecord]):
    locs = defaultdict(int)
    for r, coder, location_data in located_recs:
        if not location_data: continue
        if 'lat' not in location_data: continue
        if 'lon' not in location_data: continue
        lat = location_data['lat']
        lon = location_data['lon']
        locs['%.6f,%.6f' % (lat, lon)] += 1

    for ll, count in locs.items():
        print('%d\t%s' % (count, ll))


def output_geojson(located_recs: list[LocatedRecord]):
    features = []
    for r, coder, location_data in located_recs:
        if not location_data:
            continue  # debatable, but this is what diff_geojson.py seems to want
        feature = {
            'id': r['id'],
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [location_data['lon'], location_data['lat']]
            } if location_data else None,
            'properties': {
                'title': r['title'],
                'date': r['date'],
                'geocode': {
                    'technique': coder,
                    'lat': location_data['lat'],
                    'lng': location_data['lon'],
                    **location_data
                } if location_data else None,
                'image': {
                    'url': r['photo_url'],
                    'thumb_url': r['photo_url'],
                },
                'url': r['preferred_url'],
                'nypl_fields': {
                    'alt_title': r['alt_title'],
                    'location': r['location'],
                }
            }
        }
        features.append(feature)

    print(
        json.dumps(
            {"type": "FeatureCollection", "features": features},
            indent=2,
            sort_keys=True,
        )
    )


def output_oldto_json(located_recs: list[LocatedRecord]):
    pass
