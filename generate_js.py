#!/usr/bin/python
# Reads in a photo_id -> lat,lon mapping (from geocode_pairs.py)
# and the records and outputs a JS file.

import json
import record
import sys
from collections import defaultdict

from json import encoder
encoder.FLOAT_REPR = lambda o: format(o, '.5f')

def printJson(located_recs):
  # "lat,lon" -> list of photo_ids
  ll_to_id = defaultdict(list)

  codes = []

  for r, coder, locatable in located_recs:
    if not locatable: continue
    photo_id = r.photo_id()

    lat_lon = locatable.getLatLon()
    assert lat_lon
    lat, lon = lat_lon
    ll_to_id['%f,%f' % (lat, lon)].append(r)

  no_date = 0
  points = 0
  photos = 0
  print "var lat_lons = {"
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
      out_recs.append('[%d,%d,"%s"]' % (
        date_range[0].year, date_range[1].year, r.photo_id()))

    if out_recs:
      points += 1
      photos += len(out_recs)
      print '"%s": [%s],' % (lat_lon, ','.join(out_recs))

  print "};"

  sys.stderr.write('Dropped w/ no date: %d\n' % no_date)
  sys.stderr.write('Unique lat/longs: %d\n' % points)
  sys.stderr.write('Total photographs: %d\n' % photos)


def printRecordsJson(located_recs):
  recs = []
  for r, coder, locatable in located_recs:
    rec = {
      'id': r.photo_id(),
      'folder': r.location().replace('Folder: ', ''),
      'date': record.CleanDate(r.date()),
      'title': record.CleanTitle(r.title()),
      'description': r.description(),
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
      rec['extracted']['latlon'] = locatable.getLatLon()
      rec['extracted']['located_str'] = str(locatable)
      rec['extracted']['technique'] = coder

    recs.append(rec)
  print json.dumps(recs, indent=2)


def printRecordsText(located_recs):
  for r, coder, locatable in located_recs:
    date = record.CleanDate(r.date())
    title = record.CleanTitle(r.title())
    folder = r.location()
    if folder: folder = record.CleanFolder(folder)

    if locatable:
      loc = (str(locatable.getLatLon()) or '') + '\t' + str(locatable)
    else:
      loc = 'n/a\tn/a'

    print '\t'.join([r.photo_id(), date, folder, title, r.preferred_url, coder or 'failed', loc])
