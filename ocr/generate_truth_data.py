#!/usr/bin/env python
"""Given a list of (back) photo IDs, extract an ID -> text mapping.

This is useful for producing truth data for OCR evaluation.
"""

import json
import fileinput

from record import Record

if __name__ == '__main__':
    records: list[Record] = json.load(open('nyc/records.json'))
    back_to_front = {r['back_id']: r['id'] for r in records if r['back_id']}

    site_data = json.load(open('../oldnyc.github.io/data.json'))
    id_to_site_data = {
        r['photo_id'].split('-')[0]: r
        for r in site_data['photos']
    }

    back_id_to_text = {}
    for line in fileinput.input():
        back_id = line.strip()
        front_id = back_to_front[back_id]
        site_data = id_to_site_data[front_id]
        back_id_to_text[back_id] = site_data['text']

    print(json.dumps(back_id_to_text, indent=2))
