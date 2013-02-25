#!/usr/bin/python
'''
See comments in download-mrsids.py.

This does step #4: convert MrSID -> JPG
It's designed to run continually, checking for new .sid files.
This lets it run in parallel to a download process (download-mrsids.py)
'''

import glob
import os
import random
import subprocess
import sys
import time

cmd = 'mrsiddecode -i %s -o %s'

IMAGE_DIR = sys.argv[1]

while True:
  sid_files = glob.glob('%s/*.sid' % IMAGE_DIR)
  if sid_files:
    sid_file = random.choice(sid_files)
    jpg_file = sid_file.replace('.sid', '.jpg')

    retcode = subprocess.call(cmd % (sid_file, jpg_file), shell=True)
    if retcode == 0:
      os.remove(sid_file)
      print 'Conversion successful; removing %s' % sid_file
  else:
    time.sleep(1)
