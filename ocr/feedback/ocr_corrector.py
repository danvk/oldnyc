#!/usr/bin/env python
'''Incorporate manual feedback into OldNYC OCR.

This:
    - merges corrections to different photos with the same backing image
    - de-dupes corrections by IP
    - picks one, either based on agreement or extremeness

Input: corrections.json
Output: fixes.json
'''

# Only consider corrections after a certain time.
# Update this after pushing out new corrections.
# TODO: the second update should be on top of the first.
#       as is, it will produce a much smaller set of diffs,
#       which will adversely affect generate_static_site, which uses
#       ocr/ocr.json, which comes directly from Ocropus.
TIMESTAMP = '2015-05-27 20:19:51.707030'

import editdistance
import re
import json
from collections import defaultdict

data = json.load(open('corrections.json'))

def photo_id_to_backing_id(photo_id):
    return re.sub(r'f?(?:-[a-z])?$', 'b', photo_id)


def clean(text):
    '''Apply some mild cleaning: consolidate newlines, trim whitespace.'''
    text = re.sub(r'\n\n\n*', '\n\n', text)
    text = re.sub(r'^ *', '', text, flags=re.M)
    text = re.sub(r' *$', '', text, flags=re.M)
    return text


# Regroup based on backing_id, not photo_id.
newdata = {}
for photo_id, info in data.iteritems():
    backing_id = photo_id_to_backing_id(photo_id)
    if not backing_id in newdata:
        newdata[backing_id] = {
            'corrections': []
        }
    newdata[backing_id]['original'] = info['original']
    newdata[backing_id]['corrections'].extend(info['corrections'])

data = newdata
latest_timestamp = ''

# Sort by extremeness of edit, then de-dupe based on IP
for backing_id, info in data.iteritems():
    original = info['original'] or ''
    corrections = info['corrections']
    for c in corrections:
        c['text'] = clean(c['text'])
    corrections.sort(key=lambda c: -editdistance.eval(original, c['text']))

    ips = set()
    uniq_corrections = []
    for c in corrections:
        ip = c['user_ip']
        timestamp = c['datetime']
        if timestamp < TIMESTAMP:
            continue

        latest_timestamp = max(latest_timestamp, timestamp)
        if ip not in ips:
            ips.add(ip)
            uniq_corrections.append(c)
    data[backing_id]['corrections'] = uniq_corrections

# Choose a correction for each backing image.
# Criteria are:
# 1. Only one? Then take it.
# 2. Agreement between any pair? Use that.
# 3. Take the most extreme.
backing_id_to_fix = {}
solos, consensus, extreme = 0, 0, 0
for backing_id, info in data.iteritems():
    corrections = info['corrections']
    if len(corrections) == 0:
        continue  # nothing to do

    # pick the only fix
    if len(corrections) == 1:
        backing_id_to_fix[backing_id] = corrections[0]['text']
        solos += 1
        continue

    # pick the consensus fix
    counts = defaultdict(int)
    for c in corrections:
        counts[c['text']] += 1
    count_text = [(v, k) for k, v in counts.iteritems()]
    count_text.sort()
    count_text.reverse()
    if count_text[0][0] > 1:
        backing_id_to_fix[backing_id] = count_text[0][1]
        consensus += 1
        continue
    
    # pick the most extreme
    extreme += 1
    backing_id_to_fix[backing_id] = corrections[0]['text']

print 'Solo fixes: %4d' % solos
print 'Consensus:  %4d' % consensus
print 'Extreme:    %4d' % extreme
print ''
print 'Last timestamp: %s' % latest_timestamp

json.dump(backing_id_to_fix, open('fixes.json', 'wb'), indent=2)
