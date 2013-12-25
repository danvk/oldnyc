#!/usr/bin/python
"""Find common locations which weren't successfully geocoded."""

import json
import sys
import random
from collections import defaultdict

records = json.load(file(sys.argv[1]))

location_to_urls = defaultdict(list)

for rec in records:
  # Find records with 'folder', without 'extracted.latlon'
  if 'extracted' not in rec: continue
  e = rec['extracted']
  if 'latlon' in e: continue
  if 'folder' not in rec: continue
  if not rec['folder']: continue

  url = rec['url']
  if '\n' in rec['url']: continue
  if '\n' in rec['folder']: continue

  location_to_urls[rec['folder']].append(rec['url'])

location_by_freq = location_to_urls.keys()
location_by_freq.sort(key=lambda x: -len(location_to_urls[x]))

for loc in location_by_freq:
  urls = location_to_urls[loc]
  random.shuffle(urls)
  print '%d\t%s\t%s' % (len(urls), loc, ' '.join(urls[:5]))
