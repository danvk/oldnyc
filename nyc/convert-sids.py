#!/usr/bin/python
'''
See comments in download-mrsids.py.

This does step #4: convert MrSID -> JPG
'''

import os
import glob
import subprocess

cmd = 'mrsiddecode -i %s -o %s'

for sid_file in glob.glob('images/*.sid'):
  jpg_file = sid_file.replace('.sid', '.jpg')
  if os.path.exists(jpg_file): continue

  retcode = subprocess.call(cmd % (sid_file, jpg_file), shell=True)
  if retcode == 0:
    os.remove(sid_file)
    print 'Conversion successful; removing %s' % sid_file
