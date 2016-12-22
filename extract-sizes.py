#!/usr/bin/python
'''
Determine the sizes of a bunch of images.

Usage:
./extract-sizes.py '*.jpg' > sizes.txt

Produces a CSV file with three columns:
file-basename-no-extension,width,height
'''

import glob
import os.path
import sys
from PIL import Image


def image_size(path):
    image = Image.open(path)
    width, height = image.size
    return (width, height)

if __name__ == '__main__':
    for pattern in sys.argv[1:]:
        for path in glob.glob(pattern):
            width, height = image_size(path)
            base, _ = os.path.splitext(os.path.basename(path))
            print('%s,%d,%d' % (base, width, height))
