#!/usr/bin/env python
'''Generate a sample of images from the live site for OCR evaluation.

Uses content from ../oldnyc.github.io/by-location/*.json
'''

import csv
import json
import glob
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


if __name__ == '__main__':
    ids = read_all_ids()
    sample_ids = random.sample(ids, 100)

    # ocr.json maps "12345b" -> text. We need photo id -> text.
    back_id_to_text = json.load(open('ocr/ocr.json', 'rb'))
    id_to_text = {}
    for photo_id in sample_ids:
        back_id = 'book' + re.sub(r'f?(?:-[a-z])?$', 'b', photo_id)
        if back_id in back_id_to_text:
            id_to_text[photo_id] = back_id_to_text[back_id]
    back_id_to_text = None  # clear

    with open('tasks.csv', 'wb') as f:
        writer = csv.DictWriter(f, ['photo_id', 'record_id', 'back_id', 'ocr_text'])
        
        writer.writeheader()
        for photo_id in sample_ids:
            writer.writerow({
                'photo_id': photo_id, 
                'record_id': re.sub(r'(?:-[a-z])?$', '', photo_id),
                'back_id': re.sub(r'f?(?:-[a-z])?$', 'b', photo_id),
                'ocr_text': id_to_text.get(photo_id, 'No text')
            })
