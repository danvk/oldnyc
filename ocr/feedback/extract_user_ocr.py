#!/usr/bin/env python
'''Pull just user-generated OCR out of a CSV database dump.

Output is a JSON file mapping photo id --> manual transcription info.

Input: data.json (the published all-site file)
       user-feedback.csv
Output: corrections.json
'''

import csv
import json
import sys
from collections import defaultdict

id_to_text = {}
site_data = json.load(open('../../../oldnyc.github.io/data.json'))
last_timestamp = site_data['ocr_time']
for record in site_data['photos']:
    photo_id = record['photo_id']
    text = record['text']
    id_to_text[photo_id] = text


badwords = ['http', 'www', 'shit', 'cunt', 'fuck']

def likely_spam(text):
    for word in badwords:
        if word in text:
            return True
    return False


num_spam = 0

id_to_corrections = defaultdict(list)
for row in csv.DictReader(open('../../feedback/user-feedback.csv')):
    if not row['feedback']: continue
    if row['datetime'] <= last_timestamp: continue

    o = json.loads(row['feedback'])
    if 'text' in o:
        row['text'] = o['text']
        if likely_spam(row['text']):
            num_spam += 1
            continue
        del row['feedback']
        id_to_corrections[row['photo_id']].append(row)

sys.stderr.write('# spam: %d\n' % num_spam)

out = {}
for photo_id, corrections in id_to_corrections.iteritems():
    out[photo_id] = {
        'original': id_to_text[photo_id],
        'corrections': corrections
    }

json.dump(out, open('corrections.json', 'wb'), indent=2)
