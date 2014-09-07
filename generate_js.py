#!/usr/bin/python
# Reads in a photo_id -> lat,lon mapping (from geocode_pairs.py)
# and the records and outputs a JS file.

import json
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


def _generateJson(located_recs, lat_lon_map):
  out = {}
  # "lat,lon" -> list of photo_ids
  ll_to_id = defaultdict(list)

  codes = []
  claimed_in_map = {}

  # load a blacklist as a side input
  blacklist = loadBlacklist()

  for r, coder, location_data in located_recs:
    if not location_data: continue
    photo_id = r.photo_id()

    lat = location_data['lat']
    lon = location_data['lon']
    ll_str = '%.6f,%.6f' % (lat, lon)
    if lat_lon_map and ll_str in lat_lon_map:
      claimed_in_map[ll_str] = True
      ll_str = lat_lon_map[ll_str]
    if ll_str in blacklist: continue
    ll_to_id[ll_str].append(r)

  assert len(claimed_in_map) == len(lat_lon_map)

  no_date = 0
  points = 0
  photos = 0
  is_first = True
  for lat_lon, recs in ll_to_id.iteritems():
    sorted_recs = sorted([r for r in recs
                            if r.date_range() and r.date_range()[1]],
                         key=lambda r: r.date_range()[1])
    no_date += (len(recs) - len(sorted_recs))

    out_recs = []
    for r in sorted_recs:
      date_range = r.date_range()
      assert date_range
      assert date_range[0]
      assert date_range[1]
      out_recs.append([
        date_range[0].year, date_range[1].year, r.photo_id()])

    if out_recs:
      points += 1
      photos += len(out_recs)
      out[lat_lon] = out_recs

  sys.stderr.write('Dropped w/ no date: %d\n' % no_date)
  sys.stderr.write('Unique lat/longs: %d\n' % points)
  sys.stderr.write('Total photographs: %d\n' % photos)

  return out


def printJson(located_recs, lat_lon_map):
  data = _generateJson(located_recs, lat_lon_map)

  print "var lat_lons = "
  print json.dumps(data)


def printJsonNoYears(located_recs, lat_lon_map):
  data = _generateJson(located_recs, lat_lon_map)
  for k, v in data.iteritems():
      data[k] = [x[2] for x in v]  # drop both year elements.

  print "var lat_lons = "
  print json.dumps(data)


def printRecordsJson(located_recs):
  recs = []
  for r, coder, location_data in located_recs:
    rec = {
      'id': r.photo_id(),
      'folder': removeNonAscii(r.location().replace('Folder: ', '')),
      'date': record.CleanDate(r.date()),
      'title': removeNonAscii(record.CleanTitle(r.title())),
      'description': removeNonAscii(r.description()),
      'url': r.preferred_url,
      'extracted': {
        'date_range': [ None, None ]
      }
    }
    if r.note(): rec['note'] = r.note()

    start, end = r.date_range()
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
  print json.dumps(recs, indent=2)


def printRecordsText(located_recs):
  for r, coder, location_data in located_recs:
    date = record.CleanDate(r.date())
    title = record.CleanTitle(r.title())
    folder = r.location()
    if folder: folder = record.CleanFolder(folder)

    if location_data:
      lat = location_data['lat']
      lon = location_data['lon']
      loc = (str((lat, lon)) or '') + '\t' + location_data['address']
    else:
      loc = 'n/a\tn/a'

    print '\t'.join([r.photo_id(), date, folder, title, r.preferred_url, coder or 'failed', loc])


def printLocations(located_recs):
  locs = defaultdict(int)
  for r, coder, location_data in located_recs:
    if not locatable_data: continue
    if not 'lat' in location_data: continue
    if not 'lon' in location_data: continue
    lat = location_data['lat']
    lon = location_data['lon']
    locs['%.6f,%.6f' % (lat, lon)] += 1

  for ll, count in locs.iteritems():
    print '%d\t%s' % (count, ll)
