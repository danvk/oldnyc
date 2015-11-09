#!/usr/bin/env python
'''Pull accurate user-generated rotations out of a CSV database dump.

Output is a JSON file mapping photo id --> degrees of rotation.
Rotations are only output if they're confirmed by multiple IPs.
'''

import csv
import json
from collections import defaultdict
from datetime import datetime
from itertools import groupby


def histogram(lst):
    count_keys = [(len(list(v)), k) for k, v in groupby(sorted(lst))]
    return list(reversed(sorted(count_keys)))


last_date_ms = 0
id_to_rotation = defaultdict(list)
all_feedback = json.load(open('../../feedback/user-feedback.json'))['feedback']

for photo_id, feedback in all_feedback.iteritems():
    if 'rotate' not in feedback: continue
    rotations = feedback['rotate']

    for rotation in rotations.itervalues():
        last_date_ms = max(last_date_ms, rotation['metadata']['timestamp'])
        if 'original' in rotation:
            # This image was already confirmed as rotated & a fix was applied.
            # For now, just ignore any further rotations of it.
            continue

        row = rotation['metadata']
        row['rotate'] = rotation['rotate']
        id_to_rotation[photo_id].append(row)

last_date = datetime.fromtimestamp(last_date_ms / 1000.0).strftime('%Y-%m-%dT%H:%M:%S')

print 'Last date: %s' % last_date
print 'Rotations w/o photo ids: %d' % len(id_to_rotation[''])
del id_to_rotation['']
print 'Rotations with photo ids: %d' % len(id_to_rotation)

# TODO: a single IP rotating the image twice at multiple times is also a good signal.
id_to_confirmed = {}
num_mismatches = 0
for photo_id, rotations in id_to_rotation.iteritems():
    ip_to_max = defaultdict(int)
    for rot in rotations:
        ip = rot['user_ip']
        rot = rot['rotate']
        ip_to_max[ip] = max(rot, ip_to_max[ip])

    if len(ip_to_max) < 2:
        continue
    vals = [r % 360 for r in ip_to_max.itervalues()]
    counts = histogram(vals)

    num_plurality = counts[0][0]
    num_total = len(ip_to_max)

    if 1. * num_plurality / num_total > 0.9:
        best_rotation = counts[0][1]
        if best_rotation > 0:
            id_to_confirmed[photo_id] = best_rotation
    else:
        num_mismatches += 1
        # print '%s / %s in %s %s' % (photo_id, len(counts), len(ip_to_max), ip_to_max)


print 'mismatches: %d' % num_mismatches
print 'confirmations: %d' % len(id_to_confirmed)

json.dump({
    'last_date': last_date,
    'fixes': id_to_confirmed
}, open('rotations.json', 'wb'), indent=2)

# 1193 rotations came out of this. From a sample of 100, all were correct.
