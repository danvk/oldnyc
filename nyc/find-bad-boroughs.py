#!/usr/bin/python
"""Identify geocodes which wind up in the wrong borough for debugging."""

import json
import sys
import boroughs
import re

records = json.load(file(sys.argv[1]))

boros_re = '(New York|Manhattan|Brooklyn|Bronx|Queens|Staten Island), (?:NY|N\.Y\.)$'

for rec in records:
  if 'extracted' not in rec: continue
  e = rec['extracted']
  if 'latlon' not in e: continue
  if 'located_str' not in e: continue
  
  m = re.search(boros_re, e['located_str'])
  lat, lon = e['latlon']
  location_boro = m.group(1)
  if location_boro == 'New York':
    location_boro = 'Manhattan'

  geocode_boro = boroughs.PointToBorough(lat, lon)
  
  if location_boro != geocode_boro:
    print 'Found %s expected %s : %s' % (geocode_boro, location_boro, rec)
