#!/usr/bin/python
'''
This attempts to find bounding boxes for the pictures in a Milstein card.

The cards have a brown background and contain 1-3 images, each of which are set
on smaller, white cards.
'''

from PIL import Image, ImageFilter
import numpy as np

import cv2
import sys
import random
import math
import json
from scipy.ndimage.morphology import binary_opening, binary_closing
from scipy import ndimage

ShowImage = False
#ShowImage = True  # for debugging


def LoadAndBinarizeImage(path):
  orig_im = Image.open(path)
  w, h = orig_im.size
  im = orig_im.crop((80, 80, w - 80, h - 80))
  w, h = im.size
  im = im.resize((w / 5, h / 5), Image.ANTIALIAS)
  blur_im = im.filter(ImageFilter.BLUR)

  I = np.asarray(blur_im).copy()

  brown = np.array([178.1655574, 137.2695507, 90.26289517])
  brown[0] = np.median(I[:,:,0])
  brown[1] = np.median(I[:,:,1])
  brown[2] = np.median(I[:,:,2])

  # TODO(danvk): does removing the np.sqrt have an effect on perfomance?
  return (np.sqrt(((I - brown) ** 2).sum(2)/3) >= 20)


def ShowBinaryArray(b, title=None):
  im = Image.fromarray(255*np.uint8(b))
  im.show(im, title)

#showBinaryArray(B)
# this kills small features and introduces an 11px black border on every side
#B = binary_closing(B, structure=np.ones((11,11)))
#showBinaryArray(B)
#
#sys.exit(0)


def ProcessImage(path):
  sys.stderr.write('Processing %s...\n' % path)
  rects = []
  B = LoadAndBinarizeImage(path)
  B = ndimage.binary_fill_holes(B, structure=np.ones((5,5)))
  #ShowBinaryArray(B)

  # Following
  # http://scipy-lectures.github.com/advanced/image_processing/index.html 
  s = ndimage.generate_binary_structure(2,2)
  label_im, nb_labels = ndimage.label(B, structure=s)

  # remove small components
  # TODO(danvk): how does this work?
  sizes = ndimage.sum(B, label_im, range(nb_labels + 1))
  mask_size = sizes < 1000
  remove_pixel = mask_size[label_im]
  label_im[remove_pixel] = 0
  labels = np.unique(label_im)
  label_im = np.searchsorted(labels, label_im)

  # Use OpenCV to get info about each component.
  # http://stackoverflow.com/questions/9056646/python-opencv-find-black-areas-in-a-binary-image
  cs, _ = cv2.findContours(label_im.astype('uint8'),
      mode=cv2.RETR_LIST, method=cv2.CHAIN_APPROX_SIMPLE)

  # regions ordered by area
  regions = [(cv2.moments(c)['m00'], idx) for idx, c in enumerate(cs)]
  regions.sort()
  regions.reverse()

  for area, idx in regions:
    c = cs[idx]
    #convexI = np.zeros(label_im.shape[0:2]).astype('uint8')

    x,y,w,h       = cv2.boundingRect(c)
    ConvexHull    = cv2.convexHull(c)
    ConvexArea    = cv2.contourArea(ConvexHull)
    Solidity      = area/ConvexArea if ConvexArea else 0
    #cv2.drawContours( convexI, [ConvexHull], -1,
    #                  color=255, thickness=-1 )

    x2 = x + w
    y2 = y + h

    if w > 20 and h > 20:
      sys.stderr.write('%d x %d, solidity %f\n' % (w, h, Solidity))

    if w > 150 and h > 150 and Solidity > 0.90:
      rects.append({
        'left': 80 + 5 * x,
        'top':  80 + 5 * y,
        'right': 80 + 5 * x2,
        'bottom': 80 + 5 * y2
      })

  output = {
    'file': path,
    'rects': rects
  }

  print json.dumps(output)

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


if __name__ == '__main__':
  assert len(sys.argv) >= 2
  for path in sys.argv[1:]:
    ProcessImage(path)
