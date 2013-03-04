#!/usr/bin/python
'''Read detected rectangles and golden data and compute accuracy.

Scoring function properties:
- If you don't have the correct # of photos, you get a zero.
'''

import csv
import sys
import json

_, golden_file, actual_file = sys.argv

golden = {}
actual = {}

for line in csv.DictReader(file(golden_file)):
  path = line['image_url']
  rects = json.loads(line['rects'])
  golden[path] = rects

for line in file(actual_file):
  d = json.loads(line)
  actual[d['file']] = d['rects']

num_correct, num_wrong = 0, 0
for path in sorted(actual.keys()):
  actual_rects = actual[path]
  golden_rects = golden[path]

  if len(actual_rects) == len(golden_rects):
    num_correct += 1
  else:
    num_wrong += 1
    sys.stderr.write('%s: %d vs %d\n' % (path, len(actual_rects), len(golden_rects)))

num_total = num_correct + num_wrong
print '%d / %d = %.4f' % (num_correct, num_total, 1. * num_correct / num_total)

# Initial: 0.72 of rectangle counts correct
# w/ cv2: 0.86 (all failures are 0 vs 1)
# w/ cv2, 0.95 threshold: 0.89 (all failures are 0 vs 1) -- need better binarizing
