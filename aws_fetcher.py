#!/usr/bin/python
#
# This downloads just the images that appear on OldSF from AWS.
# It skips images that have already been downloaded.

import json
import subprocess
import os
import os.path

AWS_PATTERN = 's3://oldsf/images/%s.jpg'
LOCAL_PATTERN = 'images/%s.jpg'

# The JS file has a leading 'var foo = {' and a trailing '};' that we don't want.
js_data = file('viewer/lat-lons.js').readlines()
js_data = '{'+ ''.join(js_data[1:-1]) + '}'

photo_ids = []
lat_lons = json.loads(js_data)
for ll, image_recs in lat_lons.iteritems():
  for _, _, photo_id in image_recs:
    photo_ids.append(photo_id)

for idx, photo_id in enumerate(photo_ids):
  local_path = LOCAL_PATTERN % photo_id
  aws_path = AWS_PATTERN % photo_id

  if os.path.exists(local_path):
    print 'Skipping %s (%s already exists)' % (photo_id, local_path)
    continue

  subprocess.check_call(['s3cmd', 'get', aws_path, local_path])
  print '%d / %d (%.2f%%) completed' % (
      1 + idx, len(photo_ids), 100. * (1+idx)/len(photo_ids))
