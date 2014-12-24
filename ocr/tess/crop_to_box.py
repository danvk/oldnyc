#!/usr/bin/env python
"""Crop an image to the area covered by a box file.

The idea is that we're only interested in the portions of an image which
contain text. The other parts can be removed to get better accuracy and smaller
images.
"""

import sys

from PIL import Image, ImageFilter

from box import BoxLine, load_box_file


def find_box_extrema(boxes):
    """Returns a BoxLine with the extreme values of the boxes."""
    left = min(b.left for b in boxes)
    right = max(b.right for b in boxes)
    bottom = min(b.bottom for b in boxes)
    top = max(b.top for b in boxes)
    page = max(b.page for b in boxes)
    return BoxLine('', left, top, right, bottom, page)


def padded_box(box, pad_width, pad_height):
    """Adds some additional margin around the box."""
    return BoxLine(box.letter,
                   box.left - pad_width,
                   box.top + pad_height,
                   box.right + pad_width,
                   box.bottom - pad_height,
                   box.page)


def crop_image_to_box(im, box):
    """Returns a new image containing the pixels inside box.
    
    This accounts for BoxLine measuring pixels from the bottom up, whereas
    Image objects measure from the top down.
    """
    w, h = im.size
    box = [int(round(v)) for v in (box.left, h - box.top, box.right, h - box.bottom)]
    return im.crop(box)


if __name__ == '__main__':
    _, box_path, image_path, out_image_path = sys.argv
    boxes = load_box_file(box_path)
    big_box = find_box_extrema(boxes)
    pad_box = padded_box(big_box, 20, 20)

    im = Image.open(image_path)
    cropped_im = crop_image_to_box(im, pad_box)
    cropped_im.save(out_image_path)
