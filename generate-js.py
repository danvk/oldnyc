#!/usr/bin/python
# Reads in a photo_id -> lat,lon mapping (from geocode_pairs.py)
# and the records and outputs a JS file.

import re
import record
import sys
from collections import defaultdict

# build a photo_id -> Record dict
rs = record.AllRecords()
id_to_record = {}
for r in rs:
  id_to_record[r.photo_id()] = r

# load the list of geocodes
# format is: (photo_id)<tab>(lat,lon)[<tab>ignored...]
lines = file('/tmp/geocodes.txt').read().split('\n')

# "lat,lon" -> list of photo_ids
ll_to_id = defaultdict(list)

seen_ids = set()

codes = []
for line in lines:
  if not line: continue

  # e.g. AAB-2914<tab>37.723611,-122.400803
  photo_id = line.split("\t")[0]

  if photo_id in seen_ids:
    sys.stderr.write('Duplicated ID %s\n' % photo_id)
    continue
  seen_ids.add(photo_id)

  lat_lon = line.split("\t")[1]
  lat, lon = [float(x) for x in lat_lon.split(",")]
  ll_to_id['%f,%f' % (lat, lon)].append(photo_id)

no_date = 0
points = 0
photos = 0
print "var lat_lons = {"
for lat_lon, photo_ids in ll_to_id.iteritems():
  recs = []
  photo_ids = [id for id in photo_ids if id]
  sorted_ids = sorted([id for id in photo_ids
                          if id_to_record[id].date_range() and
                             id_to_record[id].date_range()[1]],
                      key=lambda id: id_to_record[id].date_range()[1])
  no_date += (len(photo_ids) - len(sorted_ids))
  for photo_id in sorted_ids:
    r = id_to_record[photo_id]
    date_range = r.date_range()
    # saves ~9k. could save more by doing '0.' -> '.' or ''
    # lat -= 37
    # lon += 123
    if date_range and date_range[0] and date_range[1]:
      # TODO(danvk): use a more compact date format.
      recs.append('[%d,%d,"%s"]' % (
        date_range[0].year, date_range[1].year, r.photo_id()))
    
  if recs:
    points += 1
    photos += len(recs)
    print '"%s": [%s],' % (lat_lon, ','.join(recs))

print "};"

sys.stderr.write('Dropped w/ no date: %d\n' % no_date)
sys.stderr.write('Unique lat/longs: %d\n' % points)
sys.stderr.write('Total photographs: %d\n' % photos)
