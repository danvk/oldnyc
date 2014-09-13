#!/usr/bin/env python

import os
import csv
import sys

writer = csv.DictWriter(sys.stdout, fieldnames=['photo_id', 'image'])
writer.writeheader()
for line in open('ocr/backing-images.urls.txt'):
    image_file, url = line.strip().split('\t')
    photo_id, _ = os.path.splitext(os.path.basename(image_file))
    writer.writerow({'photo_id': photo_id, 'image': image_file})
