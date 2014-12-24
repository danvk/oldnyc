#!/usr/bin/env python
"""Draw white lines where wide boxes would be split.

This encourages Tesseract to split these letter itself, by forcing them into
separate connected components.
"""

import os.path
import sys

from PIL import Image, ImageDraw

from split_wide_boxes import split_box
from box import BoxLine, load_box_file


if __name__ == '__main__':
    _, box_path, image_path = sys.argv
    im = Image.open(image_path)
    w, h = im.size
    boxes = load_box_file(box_path)
    draw = ImageDraw.Draw(im)

    line_count = 0
    for box in boxes:
        splits = split_box(box)
        if len(splits) == 1:
            continue

        # Draw white lines in all the boundary pixels.
        for subbox in splits[1:]:
            # TODO: Optimization: draw the line @ the least dark x-value
            x = subbox.left
            draw.line((x, h - box.bottom, x, h - box.top), fill='white')
            line_count += 1

    base, ext = os.path.splitext(image_path)
    out_path = base + '.separated' + ext
    im.save(out_path)

    print 'Drew %d separating lines in %s' % (line_count, out_path)
