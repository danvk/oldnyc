#!/usr/bin/python
import sys
sys.path += (sys.path[0] + '/..')

import re
import record
import cPickle
import sf_streets

rs = record.AllRecords()

street_list = file("street-list.txt").read().split("\n")
street_list = [s.lower() for s in street_list if s]

res = []
for cross_street in street_list:
  res.append(re.compile(r'\b' + cross_street + r'\b'))

for r in rs:
  # SF Streets are handled elsewhere
  if r.location().startswith("Folder: S.F. Streets-"): continue

  folder = record.CleanFolder(r.location()).lower()
  title = record.CleanTitle(r.title()).lower()
  combined = folder + " : " + title

  matches = sf_streets.extract_matches(combined, None, street_list, res)
  colon_matches = [x for x in matches if ':' in x]
  if len(matches) > 1 or colon_matches:
    print '%s\t%s\t%s' % (r.photo_id(), combined, matches)
