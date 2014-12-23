#!/usr/bin/env python
"""Crop an image to the area covered by a box file.

The idea is that we're only interested in the portions of an image which
contain text. The other parts can be removed to get better accuracy and smaller
images.
"""

import sys

from PIL import Image, ImageFilter


class BoxLine(object):
    def __init__(self, line):
        letter, left, top, right, bottom, page = line.split(' ')
        self.letter = letter
        self.left = int(left)
        self.top = int(top)
        self.right = int(right)
        self.bottom = int(bottom)
        self.page = int(page)


def load_box_file(path):
    """Load the box data in the file at path.

    Output is a list of BoxLines.
    """
    out = []
    for line in open(path):
        out.append(BoxLine(line))
    return out


if __name__ == '__main__':
    _, path = sys.argv
    boxes = load_box_file(path)
    print 'left: %d' % min(b.left for b in boxes)
    print 'right: %d' % max(b.right for b in boxes)
    print 'bottom: %d' % min(b.bottom for b in boxes)
    print 'top: %d' % max(b.top for b in boxes)
