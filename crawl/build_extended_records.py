#!/usr/bin/env python
"""Write nyc-records.extended.json. This joins NYPL API data with the OldNYC data."""

import csv
import json
from collections import Counter, defaultdict

crawl_items = json.load(open('crawl/milstein-items.json'))['items']
uuid_to_crawl = {i['uuid']: i for i in crawl_items}
crawl_items = [*uuid_to_crawl.values()]

rows = [*csv.DictReader(open('nyc/milstein.csv', encoding='latin-1'))]

photo_id_to_uuid = {
    photo_id.lower(): uuid
    for uuid, photo_id in csv.reader(open('nyc/id-uuid-mapping.csv'))
}

id_to_crawl = {}
title_to_crawl = {}
collisions = Counter()
title_collisions = Counter()
title_multi = defaultdict(list)
for r in crawl_items:
    ids = [*r['mods']['identifier']]
    for id_ in ids:
        assert isinstance(id_, str)
        if id_ in collisions:
            collisions[id_] += 1
        elif id_ in id_to_crawl:
            collisions[id_] = 2
            del id_to_crawl[id_]
        else:
            id_to_crawl[id_] = r

    titles = r['mods']['titleInfo']
    titles = [titles] if isinstance(titles, dict) else titles
    titles = {t['title'] for t in titles}
    for t in titles:
        assert isinstance(t, str)
        title_multi[t].append(r)
        if t in title_collisions:
            title_collisions[t] += 1
        elif t in title_to_crawl:
            title_collisions[t] = 2
            del title_to_crawl[t]
        else:
            title_to_crawl[t] = r

image_id_to_captures = defaultdict(list)
captures = json.load(open('crawl/milstein-captures.json'))['captures']
for capture in captures:
    image_id = capture['imageID']
    image_id_to_captures[image_id].append(capture)
image_id_to_capture = {}
for image_id, captures in image_id_to_captures.items():
    x = {json.dumps(c, indent=None, sort_keys=True) for c in captures}
    if len(x) == 1:
        image_id_to_capture[image_id] = captures[0]

extended_records = []
n_uuid = 0
n_crawl = 0
n_capture = 0
n_either = 0
for row in rows:
    r = {**row}
    photo_id = row['DIGITAL_ID']
    r['id'] = photo_id
    uuid = photo_id_to_uuid.get(photo_id)
    if uuid:
        r['uuid'] = uuid
        crawl = uuid_to_crawl.get(uuid)
        if crawl:
            r['item'] = crawl
            n_crawl += 1
    if 'item' not in r:
        record_id = row['RECORD_ID']
        record_crawl = id_to_crawl.get(record_id)
        if record_crawl:
            r['item'] = record_crawl
            if 'uuid' not in r:
                r['uuid'] = record_crawl['uuid']
    capture = image_id_to_capture.get(photo_id.upper())
    if capture:
        n_capture += 1
        r['capture'] = capture
        if 'uuid' not in r:
            r['uuid'] = capture['uuid']
    if 'item' in r or 'capture' in r:
        n_either += 1
    if 'uuid' in r:
        n_uuid += 1
    extended_records.append(r)

print(f'{n_uuid=} {n_crawl=} {n_capture=} {n_either=} / {len(rows)=}')
with open('nyc-records.extended.json', 'w') as out:
    json.dump(extended_records, out)
