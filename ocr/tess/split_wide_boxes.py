#!/usr/bin/env python
"""Split boxes that are suspicously wide.

This maps box file --> box file.
"""

import copy
import sys

from box import BoxLine, load_box_file

def split_box(box):
    """Returns a list of (possibly just one) boxes, with appropriate widths."""
    w = box.right - box.left
    h = box.top - box.bottom
    assert h > 0
    if w < 21: return [box]  # probably just a single letter.
    if h > w:  return [box]  # maybe it's just large, not wide

    num_ways = int(round(w / 12.0))
    assert num_ways > 1, w

    boxes = []
    for i in range(0, num_ways):
        b = copy.deepcopy(box)
        b.left = box.left + int(round((1.0 * i / num_ways * w)))
        b.right = box.left + int(round((1.0 * (i + 1) / num_ways * w)))
        boxes.append(b)
    return boxes


def split_boxes(boxes):
    out_boxes = []
    for box in boxes:
        out_boxes += split_box(box)
    return out_boxes


if __name__ == '__main__':
    for path in sys.argv[1:]:
        boxes = load_box_file(path)
        out_boxes = split_boxes(boxes)
        out_path = path.replace('.box', '.split.box')
        open(out_path, 'w').write('\n'.join(str(x) for x in out_boxes))
