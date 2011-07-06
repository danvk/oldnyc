#!/usr/bin/python
# Reads in a photo_id -> lat,lon mapping (from geocode_pairs.py)
# and the records and outputs a JS file.

import re
import record

# build a photo_id -> Record dict
rs = record.AllRecords()
id_to_record = {}
for r in rs:
  id_to_record[r.photo_id()] = r

# load the list of geocodes
lines = file('/tmp/pair-geocodes.txt').read().split('\n')
codes = []
for line in lines:
  if not line: continue

  # e.g. AAB-2914<tab>37.723611,-122.400803
  photo_id = line.split("\t")[0]
  lat_lon = line.split("\t")[1]
  lat, lon = [float(x) for x in lat_lon.split(",")]
  codes.append((photo_id, lat, lon))

print "var lat_lons = ["
for photo_id, lat, lon in codes:
  r = id_to_record[photo_id]
  date_range = r.date_range()
  # saves ~9k. could save more by doing '0.' -> '.' or ''
  # lat -= 37
  # lon += 123
  if date_range and date_range[0] and date_range[1]:
    # TODO(danvk): use a more compact date format.
    print '[%f,%f,"%d/%d/%d","%d/%d/%d","%s"],' % (
      lat, lon,
      date_range[0].year, date_range[0].month, date_range[0].day,
      date_range[1].year, date_range[1].month, date_range[1].day,
      r.photo_id())

print "];"
