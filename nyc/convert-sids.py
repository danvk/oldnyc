#!/usr/bin/python
'''
See comments in download-mrsids.py.

This does step #4: convert MrSID -> JPG
It's designed to run continually, checking for new .sid files.
This lets it run in parallel to a download process (download-mrsids.py)
'''

import os
import time
import glob
import subprocess

cmd = 'mrsiddecode -i %s -o %s'

while True:
  sid_files = glob.glob('images/*.sid')
  if sid_files:
    sid_file = sid_files[0]
    jpg_file = sid_file.replace('.sid', '.jpg')

    retcode = subprocess.call(cmd % (sid_file, jpg_file), shell=True)
    if retcode == 0:
      os.remove(sid_file)
      print 'Conversion successful; removing %s' % sid_file
  else:
    time.sleep(1)
