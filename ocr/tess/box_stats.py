#!/usr/bin/env python
import sys

from collections import defaultdict

from box import load_box_file

def box_widths(boxes, path):
    """Returns a dict mapping box width -> count."""
    counts = defaultdict(int)
    for box in boxes:
        width = box.right - box.left
        if 16 <= width and width <= 19:
            sys.stderr.write('%s: %s %s\n' % (width, path, box))
        counts[width] += 1
    return counts


def counts_to_list(counts):
    high_val = max(counts.keys())
    return [counts[x] for x in range(0, high_val + 1)]


if __name__ == '__main__':
    count_lists = []
    for path in sys.argv[1:]:
        boxes = load_box_file(path)
        count_lists.append(counts_to_list(box_widths(boxes, path)))

    max_width = max(len(x) for x in count_lists)

    print '\t'.join([''] + [str(x) for x in range(0, max_width)])
    for path, counts in zip(sys.argv[1:], count_lists):
        print '%s\t%s' % (path, '\t'.join(str(x) for x in counts))
