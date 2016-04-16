#!/usr/bin/env python
'''Incorporate manual feedback into OldNYC OCR.

This:
    - merges corrections to different photos with the same backing image
    - de-dupes corrections by IP
    - picks one, either based on agreement or recency

Input: corrections.json, list of rejected changes
Output: fixes.json

Usage:

    ./ocr_corrector.py (rejected_photo_id1) (rejected_photo_id2)

Things that should be improved:
1. The review UI should include user-agent, location & cookies for the
   contributor. Changes should be grouped by the contributor, for easier
   bulk-approval.
'''

import editdistance
import json
import re
import sys
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

# These changes have been rejected, presumably via the OCR review tool.
rejected_back_ids = set(map(photo_id_to_backing_id, sys.argv[1:]))

backing_id_to_photo_id = {}
site_data = json.load(open('../../../oldnyc.github.io/data.json'))
for record in site_data['photos']:
    photo_id = record['photo_id']
    back_id = re.sub(r'f?(?:-[a-z])?$', 'b', photo_id)
    backing_id_to_photo_id[back_id] = photo_id

backing_id_to_fix = {}
latest_timestamp = 0
latest_datetime = ''

# Sort by recency (most recent first), then de-dupe based on IP
for backing_id, info in data.iteritems():
    original = info['original'] or ''
    corrections = info['corrections']
    for c in corrections:
        c['text'] = clean(c['text'])
    corrections.sort(key=lambda c: c['datetime'], reverse=True)

    ips = set()
    uniq_corrections = []
    for c in corrections:
        ip = c['user_ip']
        datetime = c['datetime']
        timestamp = c['timestamp']

        latest_datetime = max(latest_datetime, datetime)
        latest_timestamp = max(latest_timestamp, timestamp)
        if ip not in ips:
            ips.add(ip)
            uniq_corrections.append(c)
    data[backing_id]['corrections'] = uniq_corrections

# Choose a correction for each backing image.
# Criteria are:
# 1. Only one? Then take it.
# 2. Agreement between any pair? Use that.
# 3. Take the most recent.
solos, consensus, recency, rejected = 0, 0, 0, 0
for backing_id, info in data.iteritems():
    corrections = info['corrections']
    if len(corrections) == 0:
        continue  # nothing to do

    if backing_id in rejected_back_ids:
        rejected += 1
        continue

    # pick the only fix
    if len(corrections) == 1:
        backing_id_to_fix[backing_id] = corrections[0]
        solos += 1
        continue

    # pick the consensus fix
    # counts = defaultdict(int)
    # for c in corrections:
    #     counts[c['text']] += 1
    # count_text = [(v, k) for k, v in counts.iteritems()]
    # count_text.sort()
    # count_text.reverse()
    # if count_text[0][0] > 1:
    #     backing_id_to_fix[backing_id] = count_text[0][1]
    #     consensus += 1
    #     continue
    
    # pick the most recent
    recency += 1
    backing_id_to_fix[backing_id] = corrections[0]

# For manual review
changes = []
for backing_id, fix in backing_id_to_fix.iteritems():
    new_text = fix['text']
    del fix['text']
    before = data[backing_id]['original']
    if before == new_text:
        continue  # this just confirms the existing text; no need to review.
    changes.append({
        'photo_id': backing_id_to_photo_id[backing_id],
        'before': data[backing_id]['original'],
        'after': new_text,
        'metadata': fix
    })

print 'Solo fixes: %4d' % solos
print 'Consensus:  %4d' % consensus
print 'Recency:    %4d' % recency
print '(Rejected): %4d' % rejected
print ''
print 'Last timestamp: %s' % latest_timestamp
print 'Last datetime: %s' % latest_datetime

json.dump({
    'fixes': backing_id_to_fix,
    'last_date': latest_datetime,
    'last_timestamp': latest_timestamp
    }, open('fixes.json', 'wb'), indent=2)

# Group changes by user for the review UI
changes.sort(key=lambda r: (r['metadata']['cookie'], r['metadata']['datetime']))

open('review/changes.js', 'w').write('var changes = %s;' %
        json.dumps(changes, indent=2, sort_keys=True))
