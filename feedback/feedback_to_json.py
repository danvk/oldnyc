#!/usr/bin/env python
"""Convert CSV feedback to JSON for Firebase import."""

import json
import csv
import sys
from collections import defaultdict
import dateutil.parser
import time

import firebase_pushid

types = set(['rotate', 'large-border', 'text', 'wrong-location', 'multiples', 'notext', 'rotate-backing', 'date', 'cut-in-half'])

def iso8601_to_millis(iso8601):
    dt = dateutil.parser.parse(iso8601)
    return int(time.mktime(dt.timetuple())*1e3 + dt.microsecond/1e3)


feedback = defaultdict(lambda: {})
push_id = firebase_pushid.PushID()


for row in csv.DictReader(open('user-feedback.csv')):
    if not row['feedback']:
        continue
    data = json.loads(row['feedback'])

    feedback_type = None
    for t in types:
        if t in data:
            assert not feedback_type
            feedback_type = t
    assert feedback_type, json.dumps(data)

    photo_id = row['photo_id']
    datetime_str = row['datetime']
    user_ip = row['user_ip']
    cookie = row['cookie']
    user_agent = row['user_agent']

    datetime_ms = iso8601_to_millis(datetime_str)

    # TODO: change between front ID and back ID depending on feedback_type

    # TODO: use push ids instead of an array

    entry = {
        'metadata': {
            'user_ip': user_ip,
            'cookie': cookie,
            'user_agent': user_agent,
            'timestamp': datetime_ms
        }
    }
    entry.update(data)

    pid = push_id.next_id(datetime_ms)

    feedback[photo_id].setdefault(feedback_type, {})
    feedback[photo_id][feedback_type][pid] = entry


json.dump({
    'feedback': feedback
}, open('feedback.json', 'wb'), indent=2, sort_keys=True)
