#!/usr/bin/env python
"""Extract individual letter images using Tesseract box files.

Usage:

    ./extract_box.py path/to/data.box path/to/data.png outputdir
"""

import errno
import os
import re
import sys

from PIL import Image

import box


def path_for_letter(output_dir, image_path, idx, letter):
    image_base = re.sub(r'\..*', '', os.path.basename(image_path))

    # The OS X file system is case insensitive.
    # This makes sure that 'a' and 'A' get mapped to different directories, and
    # that the file name is valid (i.e. doesn't have a slash in it).
    safe_char = letter.replace(r'[^a-zA-Z0-9.,"\'\[\]\(\)]', '')
    letter = '%03d-%s' % (ord(letter), safe_char)

    return os.path.join(output_dir, letter), '%s.%s.png' % (image_base, idx)


# From http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
def mkdir_p(path):
  try:
    os.makedirs(path)
  except OSError as exc: # Python >2.5
    if exc.errno == errno.EEXIST:
      pass
    else: raise


if __name__ == '__main__':
    _, box_path, image_path, output_dir = sys.argv
    boxes = box.load_box_file(box_path)
    im = Image.open(image_path)
    w, h = im.size

    for idx, box in enumerate(boxes):
        x1, x2 = box.left, box.right
        y1, y2 = h - box.top, h - box.bottom

        assert x2 > x1
        assert y2 > y1

        char_im = im.crop((x1, y1, x2, y2))
        out_dir, out_file = path_for_letter(output_dir, image_path, idx, box.letter)
        out_path = os.path.join(out_dir, out_file)
        mkdir_p(out_dir)
        char_im.save(out_path)
        print 'Wrote %s' % out_path
