#!/usr/bin/python
# Reads in a photo_id -> lat,lon mapping (from geocode_pairs.py)
# and the records and outputs a JS file.

import record
import sys
from collections import defaultdict

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
