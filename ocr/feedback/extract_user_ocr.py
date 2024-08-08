#!/usr/bin/env python
'''Pull just user-generated OCR out of a CSV database dump.

Output is a JSON file mapping photo id --> manual transcription info.

Input: data.json (the published all-site file)
       user-feedback.csv
Output: corrections.json
'''

import json
import re
import sys
from collections import defaultdict
from datetime import datetime
import dateutil.parser

id_to_text = {}
back_to_front = defaultdict(list)
site_data = json.load(open('../../../oldnyc.github.io/data.json'))
last_timestamp = site_data['ocr_time']  # e.g. "2015-09-27 15:31:07.691170"
for record in site_data['photos']:
    photo_id = record['photo_id']
    text = record['text']
    id_to_text[photo_id] = text
    back_id = re.sub(r'f?(?:-[a-z])?$', 'b', photo_id, count=1)
    if photo_id == '734557f-a':
        print(f'{photo_id} -> {back_id}')
    back_to_front[back_id].append(photo_id)

print('Last OCR update: %s' % last_timestamp)
print('back_to_front: %d' % len(back_to_front))

assert '734557b' in back_to_front

badwords = ['http', 'www', 'shit', 'cunt', 'fuck']

def likely_spam(text):
    for word in badwords:
        if word in text:
            return True
    return False


def unix_time_millis(date_str):
    dt = dateutil.parser.parse(date_str)
    epoch = datetime.utcfromtimestamp(0)
    return int((dt - epoch).total_seconds() * 1000.0)


last_time_ms = unix_time_millis(last_timestamp)
num_spam = 0

id_to_corrections = defaultdict(list)

all_feedback = json.load(open('../../feedback/user-feedback.json'))['feedback']
for back_id, feedback in all_feedback.items():
    if 'text' not in feedback: continue
    texts = feedback['text']

    for text in texts.values():
        row = text['metadata']
        if row['timestamp'] <= last_time_ms: continue

        row['text'] = text['text']
        if likely_spam(row['text']):
            print(f'Spam: {back_id} / {row}')
            num_spam += 1
            continue
        row['datetime'] = datetime.fromtimestamp(row['timestamp'] / 1000.0).strftime('%Y-%m-%dT%H:%M:%S')
        id_to_corrections[back_id].append(row)


sys.stderr.write('# spam: %d\n' % num_spam)

out = {}
for back_id, corrections in id_to_corrections.items():
    if back_id not in back_to_front:
        # This is most likely due to a photo being dropped from the site,
        # e.g. because of a geocoding update which removes it.
        print('Dropping OCR for %s' % back_id)
        continue

    photo_id = back_to_front[back_id][0]

    out[back_id] = {
        'original': id_to_text[photo_id],
        'corrections': corrections
    }

json.dump(out, open('corrections.json', 'w'), indent=2)
