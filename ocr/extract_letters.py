#!/usr/bin/env python
'''Use manually determined grids to extract individual typewritten letters.'''

import csv
from PIL import Image


def frange(x, y, jump):
  while x < y:
    yield x
    x += jump


summary = csv.DictWriter(open('ocr/transcribe/tasks.csv', 'w'),
                         fieldnames=['photo_id', 'num_rows', 'num_cols', 'char_width', 'char_height'])
summary.writeheader()

for row in csv.DictReader(open('ocr/turk/output.csv')):
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
    if rotate != 0.0: continue

    xs = list(frange(x1, x2, pixels_per_column))
    ys = list(frange(y1, y2, pixels_per_line))

    for i, x in enumerate(xs):
        for j, y in enumerate(ys):
            box = [int(round(v)) for v in (x, y, x + pixels_per_column, y + pixels_per_line)]
            letter_im = im.crop(box)
            outfile = 'ocr/images/letters/%s-%02d-%02d.png' % (photo_id, j, i)
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
