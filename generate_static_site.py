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

from dates import extract_years
from title_cleaner import is_pure_location

# Make sure the oldnyc.github.io repo is in a clean state.
git_status = subprocess.check_output('git -C ../oldnyc.github.io status --porcelain'.split(' '))
if git_status.strip():
    sys.stderr.write('Make sure the ../oldnyc.github.io repo exists and is clean.\n')
    sys.exit(1)

# TODO: replace this with JSON
# strip leading 'var popular_photos = ' and trailing ';'
popular_photos = json.loads(open('viewer/static/js/popular-photos.js', 'rb').read()[20:-2])
pop_ids = {x['id'] for x in popular_photos}

# TODO: replace this with JSON
# strip leading 'var lat_lons = ' and trailing ';'
lat_lon_to_ids = json.loads(open('viewer/static/js/nyc-lat-lons-ny.js', 'rb').read()[15:-1])

rs = record.AllRecords('nyc/photos.pickle')
id_to_record = {r.photo_id(): r for r in rs}

id_to_dims = {}
for photo_id, width, height in csv.reader(open('nyc-image-sizes.txt')):
    id_to_dims[photo_id] = (int(width), int(height))

# This file comes from an email exchange with the NYPL
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

url_hits = 0
url_misses = 0
def nypl_url(photo_id: str):
    global url_hits, url_misses
    # '726340F-a' -> '726340f'
    photo_id = re.sub(r'-.*', '', photo_id).lower()
    uuid = photo_id_to_uuid.get(photo_id)
    if not uuid:
        url_misses += 1
        sys.stderr.write(f'No UUID for {photo_id}\n')
        return None
    url_hits += 1
    return f'https://digitalcollections.nypl.org/items/{uuid}'


def decode(b):
    if isinstance(b, str):
        return b
    try:
        return b.decode('utf8')
    except UnicodeDecodeError:
        return b.decode(chardet.detect(b)['encoding'])


def make_response(photo_ids):
    response = []
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
        r = {
          'id': photo_id,
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
            r['original_title'] = original_title
        if rotation:
            r['rotation'] = rotation

        # sort the keys for more stable diffing
        # we can't just use sort_keys=True in json.dump because the photo_ids
        # in the response have a meaningful sort order.
        response.append({k: r[k] for k in sorted(r.keys())})

    # Sort by earliest date; undated photos go to the back. Use id as tie-breaker.
    response.sort(key=lambda rec: (min(rec['years']) or 'z', rec['id']))
    return response


def group_by_year(response):
    counts = defaultdict(int)
    for rec in response:
        for year in extract_years(rec['date']):
            counts[year] += 1
    return OrderedDict((y, counts[y]) for y in sorted(counts.keys()))

SORT_PRETTY = {'indent': 2, 'sort_keys': True}

all_photos = []
latlon_to_count = {}
id4_to_latlon = defaultdict(lambda: {})  # first 4 of id -> id -> latlon
textless_photo_ids = []
for latlon, photo_ids in lat_lon_to_ids.items():
    outfile = '../oldnyc.github.io/by-location/%s.json' % latlon.replace(',', '')
    photos = make_response(photo_ids)
    latlon_to_count[latlon] = group_by_year(photos)
    # indentation has minimal impact on size here.
    json.dump(photos, open(outfile, 'w'), indent=2, sort_keys=True)
    for id_ in photo_ids:
        id4_to_latlon[id_[:4]][id_] = latlon

    for response in photos:
        photo_id = response['id']
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
        del response['id']
        all_photos.append(response)

photo_ids_on_site = {photo['photo_id'] for photo in all_photos}

missing_popular = {id_ for id_ in pop_ids if id_ not in photo_ids_on_site}
sys.stderr.write(f'Missing popular: {missing_popular}\n')

timestamps = {
    # TODO: change back for new OCR fixes
    'timestamp': old_data['timestamp'],  # time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    'rotation_time': user_rotations['last_date'],
    'ocr_time': manual_ocr_fixes['last_date'],
    'ocr_ms': manual_ocr_fixes['last_timestamp']
}

# This file may be unused.
json.dump(make_response(pop_ids),
          open('../oldnyc.github.io/popular.json', 'w'), **SORT_PRETTY)

timestamps_json = json.dumps(timestamps, **SORT_PRETTY)

# This is part of the initial page load for OldNYC. File size matters.
with open('../oldnyc.github.io/lat-lon-counts.js', 'w') as f:
    lat_lons_json = json.dumps(latlon_to_count, sort_keys=True, separators=(',', ':'))
    f.write(f'''
        var lat_lons = {lat_lons_json};
        var timestamps = {timestamps_json};
    '''.strip())

# These files are all pretty small; pretty-printing and sorting isn't harmful.
for id4, id_to_latlon in id4_to_latlon.items():
    json.dump(id_to_latlon,
              open('../oldnyc.github.io/id4-to-location/%s.json' % id4, 'w'),
              **SORT_PRETTY)

# List of photos IDs without backing text.
# This is only used in the OCR correction tool, so file size is irrelevant.
json.dump({
            'photo_ids': [*sorted(textless_photo_ids)]
          },
          open('../oldnyc.github.io/notext.json', 'w'),
          **SORT_PRETTY,
          )

all_photos.sort(key=lambda photo: photo['photo_id'])

# Complete data dump -- file size does not matter.
json.dump({
            'photos': all_photos,
            **timestamps,
          },
          open('../oldnyc.github.io/data.json', 'w'),
          **SORT_PRETTY)

# TODO: Remove this one and delete from repo once it's unused.
json.dump(timestamps,
          open('../oldnyc.github.io/timestamps.json', 'w'),
          **SORT_PRETTY)

with open('../oldnyc.github.io/timestamps.js', 'w') as f:
    f.write(f'var timestamps = {timestamps_json};')

sys.stderr.write(f'Unique photos on site: {len(photo_ids_on_site)}\n')
sys.stderr.write(f'URL map hits/misses: {url_hits} / {url_misses}\n')
sys.stderr.write(f'Text-less photos: {len(textless_photo_ids)}\n')
sys.stderr.write(f'Unique lat/lngs: {len(latlon_to_count)}\n')
sys.stderr.write(f'Orphaned popular photos: {len(missing_popular)} / {len(pop_ids)}\n')
