#!/usr/bin/python
'''Read detected rectangles and golden data and compute accuracy.

Prints out three categories:
  - Declined to detect any photos (SAFE)
  - Correct # of photos detected
  - Incorrect # of photos detected
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
  f = str(d['file'])
  if 'rects' not in d:
    d['rects'] = None

  actual[f] = d


photo_frac = 0.0
def IsPassCorrect(actual_data, golden_rects):
  '''A "pass" may be a perfectly reasonable photo detection, e.g. if there's
  only a single large photo in the image.'''
  if len(golden_rects) != 1: return False

  image_size = actual_data['shape']['w'] * actual_data['shape']['h']
  r = golden_rects[0]
  photo_size = (r['x2'] - r['x1']) * (r['y2'] - r['y1'])

  global photo_frac
  photo_frac = 1. * photo_size / image_size

  return photo_frac >= 0.33


num_correct_safe = 0
num_safe, num_correct, num_wrong = 0, 0, 0
num_total = 0
for path in sorted(actual.keys()):
  if path not in golden:
    continue

  num_total += 1
  actual_rects = actual[path]['rects']
  golden_rects = golden[path]

  if actual_rects == None:
    if IsPassCorrect(actual[path], golden_rects):
      num_correct += 1
      num_correct_safe += 1
    else:
      sys.stderr.write('%s: Invalid pass %.4f\n' % (path, photo_frac))
      num_safe += 1
  elif len(actual_rects) == len(golden_rects):
    num_correct += 1
  else:
    num_wrong += 1
    sys.stderr.write('%s: %d vs %d rects (actual vs. golden)\n' % (
        path, len(actual_rects), len(golden_rects)))


print '''
Stats on %d photos

     Safe: %d (%.4f)
  Correct: %d (%.4f; %d are 'safe')
    Wrong: %d (%.4f)
''' % (num_total,
       num_safe, 1. * num_safe / num_total,
       num_correct, 1. * num_correct / num_total, num_correct_safe,
       num_wrong, 1. * num_wrong / num_total)

'''
With a 0.93 min solidity requirement:

     Safe: 3 (0.0250)
  Correct: 117 (0.9750; 5 are 'safe')
    Wrong: 0 (0.0000)

----
With a solidity > 0.98 escape hatch for big photos.

     Safe: 3 (0.0250)
  Correct: 116 (0.9667; 6 are 'safe')
    Wrong: 1 (0.0083)


----
With 10px black borders around all images before filling holes.
(average 2s/image)

     Safe: 3 (0.0250)
  Correct: 116 (0.9667; 16 are 'safe')
    Wrong: 1 (0.0083)

----
Same as below, but loosened max width and height frac to 0.8.

     Safe: 5 (0.0417)
  Correct: 113 (0.9417)
    Wrong: 2 (0.0167)

images/700347f.jpg: Invalid pass 0.1288  # washed out, image is sepia
images/712634f.jpg: Invalid pass 0.1290  # washed out
images/714985f.jpg: Invalid pass 0.1217  # total washout (??)
images/717271f.jpg: Invalid pass 0.2195  # sepia image on brown background
images/725877f.jpg: Invalid pass 0.2002  # insufficiently distinct from background
images/711032f.jpg: 2 vs 1 rects (actual vs. golden)  # rectangles overlap!!
images/720275f.jpg: 2 vs 3 rects (actual vs. golden)  # one image is sepia & has no border


----
MIN_PHOTO_SOLIDITY = 0.95
Min photo size for acceptable pass is 0.33

     Safe: 8 (0.0667)
  Correct: 110 (0.9167)
    Wrong: 2 (0.0167)

images/711131f.jpg: Invalid pass 0.1875  # incorrectly rejected as too large (0.53)
images/711932f.jpg: Invalid pass 0.2133  # same as above
images/712824f.jpg: Invalid pass 0.1805  # incorrectly rejected as too large
images/700347f.jpg: Invalid pass 0.1333  # washed out, image is sepia
images/712634f.jpg: Invalid pass 0.1335  # washed out
images/714985f.jpg: Invalid pass 0.1259  # total washout (??)
images/717271f.jpg: Invalid pass 0.2271  # sepia image on brown background
images/725877f.jpg: Invalid pass 0.2072  # insufficiently distinct from background
images/711032f.jpg: 2 vs 1 rects (actual vs. golden)  # rectangles overlap!!
images/720275f.jpg: 2 vs 3 rects (actual vs. golden)  # one image is sepia & has no border

----
Initial: 0.72 of rectangle counts correct
w/ cv2: 0.86 (all failures are 0 vs 1)
w/ cv2, 0.95 threshold: 0.89 (all failures are 0 vs 1) -- need better binarizing
'''

