#!/usr/bin/python
#
# Upload records which are complete to app engine.
#
# Usage:
# ./upload_to_appengine.py records.pickle lat-lons.js [upload url]

import random
import re
import record
import fetcher
import sys
import httplib
import MultipartPostHandler, urllib2
import json

assert 3 <= len(sys.argv) <= 4
pickle_path = sys.argv[1]
lat_lons_js_path = sys.argv[2]
upload_url = sys.argv[3] if len(sys.argv) == 4 else 'http://localhost:8080/upload'

all_rs = record.AllRecords(pickle_path)

# The JS file has a leading 'var foo = {' and a trailing '};' that we don't want.
js_data = file(lat_lons_js_path).readlines()
js_data = '{'+ ''.join(js_data[1:-1]) + '}'
lat_lons = json.loads(js_data)

ok_ids = set()
for ll, images in lat_lons.iteritems():
  for _, _, photo_id in images:
    ok_ids.add(photo_id)

rs = [r for r in all_rs if r.photo_id() in ok_ids]

sys.stderr.write('Have %d full records\n' % len(rs))

print 'Will upload via %s' % upload_url

opener = urllib2.build_opener(MultipartPostHandler.MultipartPostHandler)

for i, r in enumerate(rs):
  print '%03d Uploading %s' % (i, r.photo_id())

  # Misc late-stage cleanup:
  # Delete non-helpful "descriptions"
  desc = r.description()
  if re.match(r'^1 photographic print *: *color\.?$', desc) or \
      re.match(r'^1 photographic print *: *b&w\.?$', desc):
    desc = ''

  # remove [] and trailing period from dates.
  date = record.CleanDate(r.date())

  # remove [graphic] from titles
  title = record.CleanTitle(r.title())

  # remove leading 'Folder: ', trailing period & convert various forms of
  # dashes to a single form of slashes.
  folder = r.location()
  if folder: folder = record.CleanFolder(folder)

  q = {
    'photo_id': r.photo_id(),
    'title': title,
    'date': date,
    'folder': folder,
    'description': desc,
    'note': (r.note() or ''),
    'library_url': r.preferred_url
  }
  opener.open(upload_url, q)

# To clear the data store, run:
# import db
# qs = db.ImageRecord.all()
# for q in qs: q.delete()
