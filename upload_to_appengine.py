#!/usr/bin/python
#
# Upload records which are complete to app engine.

import random
import re
import record
import fetcher
import sys
import httplib
import MultipartPostHandler, urllib2

rs = record.AllRecords()
f = fetcher.Fetcher('images', 0)
rs = [r for r in rs if (r.photo_url and f.InCache(r.photo_url))]
random.shuffle(rs)
rs = rs[0:100]

sys.stderr.write('Have %d full records\n' % len(rs))
#upload_url = 'http://localhost:8080/upload'
upload_url = 'http://sfgeocoder.appspot.com/upload'
if len(sys.argv) > 1:
  upload_url = sys.argv[1]

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
  date = r.date().replace('[', '').replace(']','')
  if date[-1] == '.': date = date[:-1]

  # remove [graphic] from titles
  title = r.title().replace(' [graphic].', '')
  title = title.replace('[', '').replace(']','')

  # remove leading 'Folder: ', trailing period & convert various forms of
  # dashes to a single form of slashes.
  folder = r.location()
  if folder:
    if folder[-1] == '.' and not folder[-3] == '.':  # e.g. 'Y.M.C.A'
      folder = folder[:-1]
    folder = folder.replace('Folder: ', '')
    folder = re.sub(r' *- *', ' / ', folder)

  q = {
    'seq_id': str(i),
    'photo_id': r.photo_id(),
    'title': title,
    'date': date,
    'folder': folder,
    'description': desc,
    'note': (r.note() or ''),
    'library_url': r.preferred_url,
    'image': open(f.CacheFile(r.photo_url), 'rb')
  }
  opener.open(upload_url, q)

# To clear the data store, run:
# import db
# qs = db.ImageRecord.all()
# for q in qs: q.delete()
