#!/usr/bin/python
'''
Given the output of find_pictures.py, extract the individual photos.
Outputs a JSON structure containing information about what was done.
'''

import json
import os
import re
import sys
import subprocess

usage = '%s detected-photos.txt [filter] output-directory\n' % sys.argv[0]


def ExtractPhotos(d, output_dir):
  rects = d['rects'] if 'rects' in d else None
  if not rects:
    # The algorithm took a pass on this image.
    # symlink the original image into the output directory.
    output_path = os.path.join(output_dir, os.path.basename(d['file']))
    if not os.path.exists(output_path) or not os.path.samefile(d['file'], output_path):
      output = subprocess.check_output(['ln', '-sf', d['file'], output_path])
  else:
    base, ext = os.path.splitext(os.path.basename(d['file']))
    for idx, rect in enumerate(rects):
      char = chr(ord('a') + idx)
      output_path = os.path.join(output_dir, '%s-%s%s' % (base, char, ext))
      w = rect['right'] - rect['left']
      h = rect['bottom'] - rect['top']
      output = subprocess.check_output([
        'convert',
        d['file'],
        '-crop',
        '%dx%d+%d+%d' % (w, h, rect['left'], rect['top']),
        output_path
      ])
      rect['path'] = os.path.basename(output_path)


if len(sys.argv) < 3 or len(sys.argv) > 5:
  sys.stderr.write(usage)
  sys.exit(1)

photos_txt = sys.argv[1]
output_dir = sys.argv[-1]
filter_re = ''
if len(sys.argv) == 4:
  filter_re = sys.argv[2]

output = []
for line in file(photos_txt):
  d = json.loads(line)
  f = str(d['file'])
  if not re.search(filter_re, f): continue

  ExtractPhotos(d, output_dir)
  output += [d]

print json.dumps(output, indent=2)
