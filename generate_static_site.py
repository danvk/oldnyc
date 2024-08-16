#!/usr/bin/env python
'''Generate a static version of oldnyc.org consisting entirely of JSON.'''

import chardet
from collections import defaultdict, OrderedDict
import csv
import json
import record
import re
import subprocess
import sys
import time

from dates import extract_years
from title_cleaner import is_pure_location

# Make sure the oldnyc.github.io repo is in a clean state.
git_status = subprocess.check_output('git -C ../oldnyc.github.io status --porcelain'.split(' '))
if git_status.strip():
    sys.stderr.write('Make sure the ../oldnyc.github.io repo exists and is clean.\n')
    sys.exit(1)

# strip leading 'var popular_photos = ' and trailing ';'
popular_photos = json.loads(open('viewer/static/js/popular-photos.js', 'rb').read()[20:-2])
pop_ids = {x['id'] for x in popular_photos}

# strip leading 'var lat_lons = ' and trailing ';'
lat_lon_to_ids = json.loads(open('viewer/static/js/nyc-lat-lons-ny.js', 'rb').read()[15:-1])

rs = record.AllRecords('nyc/photos.pickle')
id_to_record = {r.photo_id(): r for r in rs}

id_to_dims = {}
for photo_id, width, height in csv.reader(open('nyc-image-sizes.txt')):
    id_to_dims[photo_id] = (int(width), int(height))

photo_id_to_uuid = {
    photo_id.lower(): uuid
    for uuid, photo_id in csv.reader(open('nyc/id-uuid-mapping.csv'))
}

# rotated images based on user feedback
user_rotations = json.load(open('analysis/rotations/rotations.json'))
id_to_rotation = user_rotations['fixes']

def get_back_id(photo_id):
    return re.sub(r'f?(?:-[a-z])?$', 'b', photo_id)

# Load the previous iteration of OCR. Corrections are applied on top of
# this.
old_data = json.load(open('../oldnyc.github.io/data.json', 'rb'))
old_photo_id_to_text = {r['photo_id']: r['text'] for r in old_data['photos'] if r['text']}
# manual_ocr_fixes = json.load(open('ocr/feedback/fixes.json', 'rb'))
manual_ocr_fixes = {
    'last_date': '2017-06-04T15:09:35',
    'last_timestamp': 1496603375454,
}
back_id_to_correction = {}  # lost this file
id_to_text = {}
for photo_id in id_to_record.keys():
    back_id = get_back_id(photo_id)
    if photo_id in old_photo_id_to_text:
        id_to_text[photo_id] = old_photo_id_to_text[photo_id]
    if back_id in back_id_to_correction:
        id_to_text[photo_id] = back_id_to_correction[back_id]['text']


# (This was only helpful on the initial run, when data came straight from
# Ocropus.)
# for k, txt in id_to_text.iteritems():
#     id_to_text[k] = cleaner.clean(txt)

back_id_to_text = None  # clear



def image_url(photo_id, is_thumb):
    degrees = id_to_rotation.get(photo_id)
    if not degrees:
        return 'http://oldnyc-assets.nypl.org/%s/%s.jpg' % (
            'thumb' if is_thumb else '600px', photo_id)
    else:
        return 'http://www.oldnyc.org/rotated-assets/%s/%s.%s.jpg' % (
            'thumb' if is_thumb else '600px', photo_id, degrees)


def nypl_url(photo_id: str):
    # '726340F-a' -> '726340f'
    photo_id = re.sub(r'-.*', '', photo_id).lower()
    uuid = photo_id_to_uuid.get(photo_id)
    if not uuid:
        sys.stderr.write(f'No UUID for {photo_id}\n')
        return None
    return f'https://digitalcollections.nypl.org/items/{uuid}'


def decode(b):
    if isinstance(b, str):
        return b
    try:
        return b.decode('utf8')
    except UnicodeDecodeError:
        return b.decode(chardet.detect(b)['encoding'])


def make_response(photo_ids):
    response = OrderedDict()
    for photo_id in photo_ids:
        r = id_to_record[photo_id]
        w, h = id_to_dims[photo_id]
        ocr_text = id_to_text.get(photo_id)

        # See also viewer/app.py
        title = decode(r.title())
        original_title = None
        if is_pure_location(title):
            original_title = title
            title = ''
        assert r.description() == ''
        assert r.note() == ''

        rotation = id_to_rotation.get(photo_id)
        if rotation and (rotation % 180 == 90):
            w, h = h, w

        date = re.sub(r'\s+', ' ', r.date())
        response[photo_id] = {
          'title': title,
          'date': date,
          'years': extract_years(date),
          'folder': decode(r.location()),
          'width': w,
          'height': h,
          'text': ocr_text,
          'image_url': image_url(photo_id, is_thumb=False),
          'thumb_url': image_url(photo_id, is_thumb=True),
          'nypl_url': nypl_url(photo_id),
        }
        if original_title:
            response[photo_id]['original_title'] = original_title
        if rotation:
            response[photo_id]['rotation'] = rotation

    # Sort by earliest date; undated photos go to the back.
    ids = sorted(photo_ids, key=lambda id: min(response[id]['years']) or 'z')
    return OrderedDict((id_, response[id_]) for id_ in ids)


def merge(*args):
    '''Merge dictionaries.'''
    o = {}
    for x in args:
        o.update(x)
    return o


def group_by_year(response):
    counts = defaultdict(int)
    for rec in response.values():
        for year in extract_years(rec['date']):
            counts[year] += 1
    return OrderedDict((y, counts[y]) for y in sorted(counts.keys()))

JSON_OPTS = {'indent': 2, 'sort_keys': True}

all_photos = []
latlon_to_count = {}
id4_to_latlon = defaultdict(lambda: {})  # first 4 of id -> id -> latlon
textless_photo_ids = []
for latlon, photo_ids in lat_lon_to_ids.items():
    outfile = '../oldnyc.github.io/by-location/%s.json' % latlon.replace(',', '')
    response = make_response(photo_ids)
    latlon_to_count[latlon] = group_by_year(response)  # len(response)
    json.dump(response, open(outfile, 'w'), **JSON_OPTS)
    for id_ in photo_ids:
        id4_to_latlon[id_[:4]][id_] = latlon

    for photo_id, response in response.items():
        if not response['text'] and 'f' in photo_id:
            textless_photo_ids.append(photo_id)
        lat, lon = [float(x) for x in latlon.split(',')]
        response['photo_id'] = photo_id
        response['location'] = {
            'lat': lat,
            'lon': lon
        }
        response['width'] = int(response['width'])
        response['height'] = int(response['height'])
        all_photos.append(response)

json.dump(make_response(pop_ids),
          open('../oldnyc.github.io/popular.json', 'w'), **JSON_OPTS)

with open('../oldnyc.github.io/lat-lon-counts.js', 'w') as f:
    f.write('var lat_lons = %s;' % json.dumps(latlon_to_count, **JSON_OPTS))

for id4, id_to_latlon in id4_to_latlon.items():
    json.dump(id_to_latlon,
              open('../oldnyc.github.io/id4-to-location/%s.json' % id4, 'w'),
              **JSON_OPTS)

# List of photos IDs without backing text
json.dump({
            'photo_ids': [*sorted(textless_photo_ids)]
          },
          open('../oldnyc.github.io/notext.json', 'w'),
          **JSON_OPTS,
          )

# Complete data dump
all_photos.sort(key=lambda photo: photo['photo_id'])
timestamps = {
        'timestamp': old_data['timestamp'],  # time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'rotation_time': user_rotations['last_date'],
        'ocr_time': manual_ocr_fixes['last_date'],
        'ocr_ms': manual_ocr_fixes['last_timestamp']
    }

json.dump(merge({
            'photos': all_photos,
          }, timestamps),
          open('../oldnyc.github.io/data.json', 'w'),
          **JSON_OPTS)

json.dump(timestamps,
          open('../oldnyc.github.io/timestamps.json', 'w'),
          **JSON_OPTS)
