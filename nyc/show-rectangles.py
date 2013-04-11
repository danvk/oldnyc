#!/usr/bin/python
'''
Reads in detected rectangles and shows them on the source image.
'''

from PIL import Image
import json
import sys

_, rects_path, image_path = sys.argv

path_to_rects = {}
for line in file(rects_path):
  d = json.loads(line)
  if 'rects' in d:
    path_to_rects[d['file']] = d['rects']

assert image_path in path_to_rects

rects = path_to_rects[image_path]

im = Image.open(image_path)
pix = im.load()

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

im.show()
