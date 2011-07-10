#!/usr/bin/python

# Inputs:
#   all library records
#   list of "lat,lon : category" lines
#
# Categories are prefixes, i.e. a geocode for "A / B" will apply to "A / B / C".

import sys
import record
from collections import defaultdict

catmap = {}
codes = [line.split(" : ") for line in file("cat-codes.txt").read().split("\n") if line]
for latlon, cat in codes:
  catmap[cat] = latlon

sys.stderr.write("Loaded %d category geocodes\n" % len(codes))

counts = defaultdict(int)
total = 0
rs = record.AllRecords()
for r in rs:
  cat = record.CleanFolder(r.location())
  if not cat: continue
  for geocat, lat_lon in catmap.iteritems():
    if cat.startswith(geocat):
      print "%s\t%s\tcat:%s" % (r.photo_id(), lat_lon, geocat)
      counts[geocat] += 1
      total += 1
      break

for cat in sorted(catmap.keys()):
  sys.stderr.write("  %3d %s\n" % (counts[cat], cat))
sys.stderr.write("%5d total\n" % total)
