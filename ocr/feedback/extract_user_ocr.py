#!/usr/bin/env python
'''Pull just user-generated OCR out of a CSV database dump.

Output is a JSON file mapping photo id --> manual transcription info.

Input: data.json (the published all-site file)
       user-feedback.csv
Output: corrections.json
'''

import csv
import json
from collections import defaultdict

id_to_text = {}
records = json.load(open('../../../oldnyc.github.io/data.json'))
for record in records:
    photo_id = record['photo_id']
    text = record['text']
    id_to_text[photo_id] = text

id_to_corrections = defaultdict(list)
for row in csv.DictReader(open('user-feedback.csv')):
    if not row['feedback']: continue
    o = json.loads(row['feedback'])
    if 'text' in o:
        row['text'] = o['text']
        del row['feedback']
        id_to_corrections[row['photo_id']].append(row)

out = {}
for photo_id, corrections in id_to_corrections.iteritems():
    out[photo_id] = {
        'original': id_to_text[photo_id],
        'corrections': corrections
    }

json.dump(out, open('corrections.json', 'wb'), indent=2)
