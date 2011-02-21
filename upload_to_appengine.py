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
opener = urllib2.build_opener(MultipartPostHandler.MultipartPostHandler)

for i, r in enumerate(rs):
  print '%03d Uploading %s' % (i, r.photo_id())

  q = {
    'id': r.photo_id(),
    'title': r.title(),
    'date': r.date(),
    'location': r.location(),
    'description': r.description(),
    'photo_url': r.photo_url,
    'image': open(f.CacheFile(r.photo_url), 'rb')
  }
  opener.open(upload_url, q)
  break
