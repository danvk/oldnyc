#!/usr/bin/env python
"""Print out a sample of photo IDs without location information."""

import sys
import json
import random


if __name__ == '__main__':
    n = int(sys.argv[1])
    site_photos = json.load(open('../oldnyc.github.io/data.json'))['photos']
    located_ids = {photo['photo_id'].split('-')[0] for photo in site_photos}
    all_ids = [r['id'] for r in json.load(open('nyc/records.json'))]
    unlocated_ids = [id for id in all_ids if id not in located_ids]
    random.shuffle(unlocated_ids)
    for id in unlocated_ids[:n]:
        print(id)
