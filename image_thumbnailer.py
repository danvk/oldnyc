#!/usr/bin/python

import record
import fetcher
import os

rs = record.AllRecords()
f = fetcher.Fetcher('images', 0)
rs = [r for r in rs if (r.photo_url and f.InCache(r.photo_url))]

for idx, r in enumerate(rs):
  in_image = f.CacheFile(r.photo_url)
  out_image = 'thumbnails/%s.jpg' % r.photo_id()
  cmd = 'convert %s -resize 200x200 %s' % (in_image, out_image)
  print '%05d %s' % (idx, cmd)
  os.system(cmd)
