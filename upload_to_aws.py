#!/usr/bin/python
"""
This uploads full images to S3.
"""

import record
import fetcher
import os

rs = record.AllRecords()
f = fetcher.Fetcher('images', 0)
rs = [r for r in rs if (r.photo_url and f.InCache(r.photo_url))]

for idx, r in enumerate(rs):
  in_image = f.CacheFile(r.photo_url)
  out_image = 's3://oldsf/images/%s.jpg' % r.photo_id()
  cmd = 's3cmd put %s %s' % (in_image, out_image)
  print '%05d %s' % (idx, cmd)
  os.system(cmd)
