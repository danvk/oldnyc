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
from skimage.transform import hough, probabilistic_hough
from skimage.filter import canny, threshold_otsu, sobel
from skimage.feature import harris
from scipy import optimize

import matplotlib.pyplot as plt

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

B = 255 - 255 * (np.sqrt(((I - Brown) ** 2).sum(2)/3) < 20)


def randomWhitePixel(ary):
  w, h = ary.shape
  while True:
    x, y = int(random.uniform(0, w)), int(random.uniform(0, h))
    x = min(x, w - 1)
    y = min(y, h - 1)
    if ary[x][y]:
      return x, y


def findWhiteRect(ary):
  # Pick a random pixel to start with a 1x1 rect.
  w, h = ary.shape[0:2]
  x, y = randomWhitePixel(ary)
  x1, y1, x2, y2 = x, y, x, y

  # Keep expanding in each direction until it's no longer helpful.
  while True:
    expanded = False
    # Expand left
    if x1 >= 5:
      c = ary[x1-5:x1, y1:y2+1].sum()
      if c:
        x1 -= 5
        expanded = True
    # Expand up
    if y1 >= 5:
      c = ary[x1:x2+1, y1-5:y1].sum()
      if c:
        y1 -= 5
        expanded = True
    # Expand right
    if x2 < w - 5:
      c = ary[x2+1:x2+6, y1:y2+1].sum()
      if c:
        x2 += 5
        expanded = True
    # Expand down
    if y2 < h - 5:
      c = ary[x1:x2+1, y2+1:y2+6].sum()
      if c:
        y2 += 5
        expanded = True

    if not expanded:
      break

  return x1, y1, x2, y2


# Keep looking for white rectangles until the image is 90% white.
# Only record the ones which are sufficiently large.
rects = []
print B.mean()
while True:
  r = findWhiteRect(B)
  x1, y1, x2, y2 = r
  if x2 - x1 > 150 and y2 - y1 > 150:
    rects.append(r)
  B[x1:x2+1, y1:y2+1] = 0

  print '%s -> %f' % (r, B.mean())

  if B.mean() < 0.10 * 255:
    break


pix = orig_im.load()
for x1, y1, x2, y2 in rects:
  ox1 = int(x1 * 5 + 80)
  ox2 = int(x2 * 5 + 80)
  oy1 = int(y1 * 5 + 80)
  oy2 = int(y2 * 5 + 80)

  for x in xrange(ox1, ox2 + 1):
    pix[oy1, x] = (255, 0, 0)
    pix[oy2, x] = (255, 0, 0)
  for y in xrange(oy1, oy2 + 1):
    pix[y, ox1] = (255, 0, 0)
    pix[y, ox2] = (255, 0, 0)

orig_im.show()
