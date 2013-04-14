#!/usr/bin/python
'''Converts the output of extract-images.py into a nice JSON object.

Output looks like:
  {
    '702370f.jpg': {
      '702370f-1.jpg': { top: 10, left: 20, width: 400, height: 300},
      '702370f-2.jpg': { top: 10, left: 20, width: 400, height: 300},
      '702370f-3.jpg': { top: 10, left: 20, width: 400, height: 300}
    }
  }
'''

import os
import json
import fileinput

out = {}
for line in fileinput.input():
  d = json.loads(line)
  entry = {}
  if 'rects' in d:
    for r in d['rects']:
      entry[os.path.basename(r['file'])] = {
        'top': r['top'],
        'left': r['left'],
        'width': r['right'] - r['left'],
        'height': r['bottom'] - r['top']
      }
  out[os.path.basename(d['file'])] = entry

print json.dumps(out, indent=2, sort_keys=True)
