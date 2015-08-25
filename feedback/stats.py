#!/usr/bin/env python
"""Print out stats on user feedback."""

import json
import csv
import sys
from collections import defaultdict

# Ignore feedback from before this date.
start_date = '2015-06-01'

skipped = 0
count = 0

types = set(['rotate', 'large-border', 'text', 'wrong-location', 'multiples', 'notext', 'rotate-backing', 'date', 'cut-in-half'])
type_counts = defaultdict(int)
date_counts = defaultdict(int)

for row in csv.DictReader(open('user-feedback.csv')):
    dt = row['datetime']
    if dt < start_date:
        skipped += 1
        continue
    count += 1

    if not row['feedback']:
        continue
    data = json.loads(row['feedback'])

    has_payload = False
    for t in types:
        if t in data:
            assert not has_payload
            type_counts[t] += 1
            has_payload = True
    assert has_payload, json.dumps(data)

    date_counts[dt[:10]] += 1

sys.stderr.write('Skipped %d records\n' % skipped)
sys.stderr.write('Included %d records\n' % count)
sys.stderr.write('Type counts:\n%s\n' % json.dumps(type_counts, indent=2, sort_keys=True))

sys.stderr.write('By date:\n%s\n' % json.dumps(date_counts, indent=2, sort_keys=True))
