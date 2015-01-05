#!/usr/bin/env python
"""Draw white lines where wide boxes would be split.

This encourages Tesseract to split these letter itself, by forcing them into
separate connected components.
"""

import os.path
import sys

from PIL import Image, ImageDraw
import numpy as np

from split_wide_boxes import split_box
from box import BoxLine, load_box_file


if __name__ == '__main__':
    _, box_path, image_path = sys.argv
    im = Image.open(image_path)
    w, h = im.size
    boxes = load_box_file(box_path)
    draw = ImageDraw.Draw(im)

    px = np.asarray(im)

    line_count = 0
    for box in boxes:
        y1 = h - box.top
        y2 = h - box.bottom
        x1 = box.left
        x2 = box.right

        # reinforce existing vertical splits
        # draw.line((x1, y2, x2, y2), fill='white')

        splits = split_box(box)
        if len(splits) == 1:
            continue

        # Draw white lines in all the boundary pixels.
        for subbox in splits[1:]:
            x1 = subbox.left
            x2 = subbox.right
            # TODO: Optimization: draw the line @ the least dark x-value
            counts = [(-np.sum(px[y1:y2+1, x1 + dx]), x1 + dx) for dx in (-2, -1, 0, 1, 2)]
            #print '%d, %d, %d %r' % (x, y1, y2, counts)
            counts.sort()
            x = counts[0][1]
            draw.line((x, y2, x, y1), fill='rgb(246,246,246)')
            line_count += 1

    base, ext = os.path.splitext(image_path)
    out_path = base + '.separated' + ext
    im.save(out_path)

    print 'Drew %d separating lines in %s' % (line_count, out_path)
