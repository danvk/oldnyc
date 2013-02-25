#!/usr/bin/python
from PIL import Image, ImageFilter
import numpy as np
import sys
import json
import os
import csv

rect_map = {}
for row in csv.DictReader(file('testdata/outputs.csv')):
  rect_map[row['image_url']] = json.loads(row['rects'])

i = 0
for path, rects in rect_map.iteritems():
  orig_im = Image.open(path)
  w, h = orig_im.size

  pix = orig_im.load()
  for r in rects:
    x1 = r['x1']
    y1 = r['y1']
    x2 = r['x2']
    y2 = r['y2']

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
  i += 1
