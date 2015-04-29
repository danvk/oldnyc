#!/usr/bin/env python
'''Generate a sample of images from the live site for OCR retraining.

Uses content from ../oldnyc.github.io/by-location/*.json
'''

import csv
import json
import glob
import os
import random
import re


def read_ids(path):
    data = json.load(open(path))
    return data.keys()


def read_all_ids():
    ids = []
    for path in glob.glob('../oldnyc.github.io/by-location/*.json'):
        ids.extend(read_ids(path))
    return ids


def read_all_backing_ids():
    images = glob.glob('/Users/danvk/Desktop/high-res-ocr/cropped/*.png')
    return {re.sub(r'b.*', 'b', os.path.basename(path)) for path in images}


def front_to_back(front_id):
    return re.sub(r'f?(?:-[a-z])?$', 'b', front_id)


if __name__ == '__main__':
    backing_ids = read_all_backing_ids()
    ids = [front_to_back(x) for x in read_all_ids()]
    ids = [x for x in ids if x in backing_ids]
    sample_ids = list(set(random.sample(ids, 2500)))

    random.shuffle(sample_ids)
    print '\n'.join(sample_ids[:2000])
