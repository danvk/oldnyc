#!/usr/bin/env python
"""Extract text from ocropus outputs.

This concatenates the individual text fragments, from left to right and then
top to bottom.

It orders the fragments by y-midpoint, then uses x coordinates to order
overlapping fragments.

Input is an hOCR file (from ocropus-hocr).
Output is text, printed to stdout.
"""

import re
import sys

from bs4 import BeautifulSoup


def overlapping(a, b):
    """Two lines are overlapping if >50% of either is in the other."""
    overlap = min(a['y2'], b['y2']) - max(a['y1'], b['y1'])
    height = min(a['y2'] - a['y1'], b['y2'] - b['y1'])
    return 1.0 * overlap / height > 0.5


def sort_lines(lines):
    lines = lines[:]

    # First, sort by y-midpoint
    lines.sort(key=lambda line: (line['y1'] + line['y2']) * 0.5)

    # If a line is entirely to the left of the one preceding it, and they
    # overlap vertically, then they're out of order.
    i = 0
    while i < len(lines) - 1:
        a = lines[i]
        b = lines[i + 1]
        if b['x2'] < a['x1'] and overlapping(a, b):
            lines[i], lines[i + 1] = b, a
            i = 0
        else:
            i += 1

    for a, b in zip(lines[:-1], lines[1:]):
        if overlapping(a, b):
            b['continuation'] = True

    return lines


def hocr_to_lines(hocr_path):
    lines = []
    soup = BeautifulSoup(file(hocr_path))
    for tag in soup.select('.ocr_line'):
        m = re.match(r'bbox (-?\d+) (-?\d+) (-?\d+) (-?\d+)', tag.get('title'))
        assert m
        x0, y0, x1, y1 = (int(v) for v in m.groups())
        lines.append({
            'text': tag.text,
            'x1': x0,
            'y1': y1,
            'x2': x1,
            'y2': y0  # note swap
        })
    # hOCR specifies that y-coordinates are from the bottom.
    # We fix that here. We don't know the height of the image, so we use the
    # largest y-value in its place.
    h = max(line['y1'] for line in lines)
    for line in lines:
        line['y1'] = h - line['y1']
        line['y2'] = h - line['y2']
    return lines


if __name__ == '__main__':
    _, hocr_path = sys.argv
    lines = hocr_to_lines(hocr_path)
    lines = sort_lines(lines)

    output = ''
    for idx, line in enumerate(lines):
        if idx > 0:
            if line.get('continuation'):
                output += '  '
            else:
                output += '\n'
        if 'text' in line:
            output += line['text']

    print output
