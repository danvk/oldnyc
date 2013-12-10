#!/usr/bin/python
'''
Adds neighborhoods to a records.json file, in the 'extracted' section of each
record.

A neighborhood gets added to all geocoded records. If we can't match a
neighborhood, it gets set to 'Unknown'.
'''

import boroughs
import sys
import json
from collections import defaultdict

neighborhood_to_counts = defaultdict(int)

records = json.load(file(sys.argv[1]))
for idx, rec in enumerate(records):
  if idx % 2000 == 0:
    sys.stderr.write('%d / %d...\n' % (idx, len(records))

  if 'extracted' not in rec:
    continue
  e = rec['extracted']
  if 'latlon' not in e:
    continue
  lat, lon = e['latlon']

  n = boroughs.PointToNeighborhood(lat, lon)
  if not n:
    n = 'Unknown'
  neighborhood_to_counts[n] += 1
  rec['extracted']['neighborhood'] = n

for k, v in neighborhood_to_counts.iteritems():
  print '%s\t%s' % (v, k)

json.dump(records, file('records+neighborhoods.json', 'w'), indent=2)
