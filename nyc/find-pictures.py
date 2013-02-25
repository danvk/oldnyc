#!/usr/bin/python
'''
This attempts to find bounding boxes for the pictures in a Milstein card.

The cards have a brown background and contain 1-3 images, each of which are set
on smaller, white cards.
'''

from PIL import Image, ImageFilter
import numpy as np

import sys
import random
import math
import json
from scipy.ndimage.morphology import binary_opening, binary_closing

ShowImage = False
ShowImage = True  # for debugging

Brown = np.array([178.1655574, 137.2695507, 90.26289517])
def isBrown(pixel):
  global Brown
  rmse = math.sqrt(((pixel - Brown) ** 2).sum() / 3)
  return rmse < 20


assert len(sys.argv) == 2

orig_im = Image.open(sys.argv[1])
w, h = orig_im.size
im = orig_im.crop((80, 80, w - 80, h - 80))
w, h = im.size
im = im.resize((w / 5, h / 5), Image.ANTIALIAS)
blur_im = im.filter(ImageFilter.BLUR)

I = np.asarray(blur_im).copy()
Brown[0] = np.median(I[:,:,0])
Brown[1] = np.median(I[:,:,1])
Brown[2] = np.median(I[:,:,2])

# TODO(danvk): does removing the np.sqrt have an effect on perfomance?
B = (np.sqrt(((I - Brown) ** 2).sum(2)/3) < 20)

def showBinaryArray(b, title=None):
  im = Image.fromarray(255*np.uint8(b))
  im.show(B, title)

# showBinaryArray(B)
# this kills small features and introduces an 11px black border on every side
B = binary_closing(B, structure=np.ones((11,11)))
showBinaryArray(B)

sys.exit(0)


def randomWhitePixel(ary):
  h, w = ary.shape
  while True:
    x, y = int(random.uniform(0, w)), int(random.uniform(0, h))
    x = min(x, w - 1)
    y = min(y, h - 1)
    if ary[y][x]:
      return x, y


def findWhiteRect(ary):
  # Pick a random pixel to start with a 1x1 rect.
  h, w = ary.shape[0:2]
  x, y = randomWhitePixel(ary)
  x1, y1, x2, y2 = x, y, x, y

  # Keep expanding in each direction until it's no longer helpful.
  while True:
    expanded = False
    # Expand up
    if y1 >= 5:
      c = ary[y1-5:y1, x1:x2+1].sum()
      if c:
        y1 -= 5
        expanded = True
    # Expand left
    if x1 >= 5:
      c = ary[y1:y2+1, x1-5:x1].sum()
      if c:
        x1 -= 5
        expanded = True
    # Expand down
    if y2 < h - 5:
      c = ary[y2+1:y2+6, x1:x2+1].sum()
      if c:
        y2 += 5
        expanded = True
    # Expand right
    if x2 < w - 5:
      c = ary[y1:y2+1, x2+1:x2+6].sum()
      if c:
        x2 += 5
        expanded = True

    if not expanded:
      break

  return x1, y1, x2, y2


# Keep looking for white rectangles until the image is 90% white.
# Only record the ones which are sufficiently large.
rects = []
sys.stderr.write('Image mean: %f\n' % B.mean())
while True:
  r = findWhiteRect(B)
  x1, y1, x2, y2 = r
  counted = False
  if x2 - x1 > 150 and y2 - y1 > 150:
    rects.append({
      'left': 80 + 5 * x1,
      'top':  80 + 5 * y1,
      'right': 80 + 5 * x2,
      'bottom': 80 + 5 * y2
    })
    counted = True
  B[y1:y2+1, x1:x2+1] = 0

  sys.stderr.write('%s %s -> %f\n' % ('+' if counted else '-', r, B.mean()))

  if B.mean() < 0.10 * 255:
    break

print json.dumps(rects)


if ShowImage:
  pix = orig_im.load()
  for r in rects:
    x1 = r['left']
    y1 = r['top']
    x2 = r['right']
    y2 = r['bottom']

    for x in xrange(x1, x2 + 1):
      pix[x, y1] = (255, 0, 0)
      pix[x, y2] = (255, 0, 0)
      pix[x, y1 + 1] = (255, 0, 0)
      pix[x, y2 - 1] = (255, 0, 0)
    for y in xrange(y1, y2 + 1):
      pix[x1, y] = (255, 0, 0)
      pix[x2, y] = (255, 0, 0)
      pix[x1 + 1, y] = (255, 0, 0)
      pix[x2 - 1, y] = (255, 0, 0)

  orig_im.show()
