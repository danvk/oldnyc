#!/usr/bin/env python
"""Split single images in records.json into multiple records in photos.json."""

import os
import sys
import copy
import json

from record import Record

if __name__ == '__main__':
    assert len(sys.argv) == 4, 'Usage: %s records.json crops.json photos.json'
    _, records_json, crops_json, out_json = sys.argv

    rs: list[Record] = json.load(open(records_json))
    expansions = json.load(open(crops_json))

    skipped = 0
    num_images, num_photos = 0, 0

    out = []
    for idx, r in enumerate(rs):
        digital_id = r['id']
        image_file = '%s.jpg' % digital_id
        expansion = expansions.get(image_file) or {'crops': {}}
        # if not expansion:
        #     # XXX: why skip any images?
        #     # skipped += 1
        #     # sys.stderr.write(f'Skipping {digital_id}\n')
        #     continue

        num_images += 1

        crops = expansion['crops']
        if len(crops) == 0:
            # r.thumbnail_url = image_file
            r['photo_url'] = image_file
            out.append(r)
            num_photos += 1
        else:
            for photo_file in crops.keys():
                new_r = copy.deepcopy(r)
                new_id, _  = os.path.splitext(photo_file)
                new_r['id'] = new_id
                new_r['photo_url'] = photo_file
                out.append(new_r)
                num_photos += 1

        if num_photos % 1000 == 0:
            sys.stderr.write('Processed %d images -> %d photos\n' % (num_images, num_photos))

    sys.stderr.write('Skipped %d records\n' % skipped)
    with open(out_json, 'w') as f:
        json.dump(out, f, separators=(',', ':'))
