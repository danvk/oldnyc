#!/usr/bin/python
'''
Reads in the output of find_pictures.py and prints out some statistics.
'''

from collections import defaultdict
import fileinput
import json

rect_counts = [0] * 10

for line in fileinput.input():
  d = json.loads(line)
  f = str(d['file'])
  if 'rects' not in d:
    rect_counts[0] += 1
  else:
    n = len(d['rects'])
    rect_counts[n] += 1
    # if n > 5:
    #   print '%d %s' % (n, d['file'])


print '\n'.join(['%d: %d' % x for x in enumerate(rect_counts)])
