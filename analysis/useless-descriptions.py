#!/usr/bin/python
# Checks how many images have non-helpful bits in their descriptions, e.g.:
# 1 photographic print: color.
# 1 photographic print: b&w.

import sys
sys.path += (sys.path[0] + '/..')

import re
import record
from collections import defaultdict

catch_phrases = [
  '1 photographic print: color.',  # 435
  '1 photographic print: b&w',     # 29775
  '1 photographic print : b&w',
  '1 photographic print  b&w',
  '1 photographic print : color'
]

rs = record.AllRecords()
counts = defaultdict(int)

x = 0
for r in rs:
  desc = r.description()
  #counted = False
  #for c in catch_phrases:
  #  if c in desc:
  #    counts[c] += 1
  #    counted = True
  # if not counted:
  #   print desc
  if re.match(r'^1 photographic print *: *color\.?$', desc) or \
      re.match(r'^1 photographic print *: *b&w\.?$', desc):
    x += 1
  else:
    print desc

print '%d' % x
print '%s' % counts
