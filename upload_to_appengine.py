#!/usr/bin/python
#
# Upload records which are complete to app engine.

import random
import record
import fetcher
import sys
import httplib
import MultipartPostHandler, urllib2

rs = record.AllRecords()
f = fetcher.Fetcher('images', 0)
rs = [r for r in rs if (r.photo_url and f.InCache(r.photo_url))]

sys.stderr.write('Have %d full records\n' % len(rs))
upload_url = 'http://localhost:8080/upload'
if len(sys.argv) > 1:
  upload_url = sys.argv[1]

print 'Will upload via %s' % upload_url

opener = urllib2.build_opener(MultipartPostHandler.MultipartPostHandler)

for i, r in enumerate(rs):
  print '%03d Uploading %s' % (i, r.photo_id())

  desc = r.description()
  if r.note():
    desc += '\n\n' + r.note()

  q = {
    'seq_id': str(i),
    'photo_id': r.photo_id(),
    'title': r.title(),
    'date': r.date(),
    'location': r.location(),
    'description': desc,
    'photo_url': r.photo_url,
    'image': open(f.CacheFile(r.photo_url), 'rb')
  }
  opener.open(upload_url, q)

# To clear the data store, run:
# import db
# qs = db.ImageRecord.all()
# for q in qs: q.delete()
