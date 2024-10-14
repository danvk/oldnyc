#!/usr/bin/env python
import json
import re

data = json.load(open('../oldnyc.github.io/data.json'))

back_ids = set()
back_ids_with_text = set()

def get_back_id(photo_id):
    return re.sub(r'f?(?:-[a-z])?$', 'b', photo_id)

for record in data['photos']:
    back_id = get_back_id(record['photo_id'])
    back_ids.add(back_id)
    if record.get('text'):
        back_ids_with_text.add(back_id)

print("Total records: %d" % len(back_ids))
print("    with text: %d" % len(back_ids_with_text))
