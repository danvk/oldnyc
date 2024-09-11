#!/usr/bin/env python
"""Download a random sample of images from the OCR backs bucket."""

import os
import random
import json
from collections import Counter

import requests
import tqdm

from record import Record

# OUT_DIR = '/Users/danvk/Documents/oldnyc/ocrbacks'
OUT_DIR = '/Volumes/teradan/Milstein Images/ocrbacks'

URL1 = 'https://oldnyc-assets-labs-nypl-org.s3.amazonaws.com/ocrbacks/successes/%s.reconstructed.jpg'
URL2 = 'https://oldnyc-assets-labs-nypl-org.s3.amazonaws.com/ocrbacks/fails/%s.original.jpg'


if __name__ == '__main__':
    records: list[Record] = json.load(open('nyc/records.json'))
    random.shuffle(records)

    results = Counter()
    for i, r in enumerate(tqdm.tqdm(records)):
        back_id = r['back_id']
        if not back_id:
            continue
        exists = False
        for url_pat in (URL1, URL2):
            url = url_pat % back_id
            out_path = os.path.join(OUT_DIR, os.path.basename(url))
            if os.path.exists(out_path):
                exists = True
        if exists:
            continue

        result = None
        for url_pat in (URL1, URL2):
            url = url_pat % back_id
            out_path = os.path.join(OUT_DIR, os.path.basename(url))
            r = requests.get(url_pat % back_id)
            if r.status_code != 200:
                # print(f'{back_id} failed on {url}')
                continue
            result = url_pat
            with open(out_path, 'wb') as out:
                out.write(r.content)
            # print(f'{back_id} matched at {url}')
            results[url_pat] += 1
            results['hit'] += 1
            break

        # print(f'{back_id}\t{result}')

        if not result:
            # print(f'No backing image for {back_id}')
            results['fail'] += 1
        if i % 100 == 0:
            print(results)

    print(results)
