#!/usr/bin/env python
'''Use manually determined grids to extract individual typewritten letters.'''

import csv
import sys

from PIL import Image


def frange(x, y, jump):
  while x < y:
    yield x
    x += jump


summary = csv.DictWriter(open('ocr/transcribe/tasks.csv', 'w'),
                         fieldnames=['photo_id', 'num_rows', 'num_cols', 'char_width', 'char_height'])
summary.writeheader()

for row in csv.DictReader(open('ocr/turk/output.csv')):
    #if row['photo_id'] != '700078f': continue

    im = Image.open(row['image'])
    photo_id = row['photo_id']
    pixels_per_column = float(row['pp-col'])
    pixels_per_line = float(row['pp-line'])
    x1 = float(row['x1'])
    y1 = float(row['y1'])
    x2 = float(row['x2'])
    y2 = float(row['y2'])
    rotate = float(row['rotate-deg'])

    # punt on these for now
    if rotate != 0.0:
        # Positive value = image is rotated clockwise from vertical.
        # The lines are rotated around the center of (x1,y1)-(x2,y2) rect.
        im = im.rotate(rotate)

    # shift boundaries from baselines to the base of the font's descenders.
    shift = pixels_per_line * 0.2
    xs = list(frange(x1, x2, pixels_per_column))
    ys = list(frange(y1 + shift, y2 + shift, pixels_per_line))

    for j, y in enumerate(ys):
        box = [int(round(v)) for v in [
            xs[0],
            y,
            xs[-1] + pixels_per_line,
            y + pixels_per_line
        ]]
        row_im = im.crop(box)
        outfile = 'ocr/large-images/rows/%s-%02d.png' % (photo_id, j)
        row_im.save(outfile)

        for i, x in enumerate(xs):
            box = [int(round(v)) for v in (x, y, x + pixels_per_column, y + pixels_per_line)]
            letter_im = im.crop(box)
            outfile = 'ocr/large-images/letters/%s-%02d-%02d.png' % (photo_id, j, i)
            letter_im.save(outfile)

    summary.writerow({
        'photo_id': photo_id,
        'num_rows': len(ys),
        'num_cols': len(xs),
        'char_width': pixels_per_column,
        'char_height': pixels_per_line
        })

    # im.show()  # writes to a temp file, opens Preview
    #break

# this one has a different font:
# ocr/large-images/700276bu.jpg,700276f,41.90000000000001,101,-0.42967714209876995,1168.0000305175781,2900.925048828125,1717.9998779296875,2228.181396484375
