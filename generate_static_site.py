#!/usr/bin/env python
'''Generate a static version of oldnyc.org consisting entirely of JSON.'''

import chardet
from collections import defaultdict, OrderedDict
import csv
import json
import record
import re
from distutils.dir_util import copy_tree
from shutil import copyfile
import os

from ocr import cleaner
import title_cleaner


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

# rotated images based on user feedback
user_rotations = json.load(open('analysis/rotations/rotations.json'))
id_to_rotation = user_rotations['fixes']

# Load the previous iteration of OCR. Corrections are applied on top of
# this.
old_data = json.load(open('../oldnyc.github.io/data.json', 'rb'))
old_photo_id_to_text = {r['photo_id']: r['text'] for r in old_data['photos'] if r['text']}
manual_ocr_fixes = json.load(open('ocr/feedback/fixes.json', 'rb'))
back_id_to_correction = manual_ocr_fixes['fixes']
id_to_text = {}
for photo_id in id_to_record.iterkeys():
    back_id = re.sub(r'f?(?:-[a-z])?$', 'b', photo_id)
    book_id = 'book' + back_id
    if photo_id in old_photo_id_to_text:
        id_to_text[photo_id] = old_photo_id_to_text[photo_id]
    if back_id in back_id_to_correction:
        id_to_text[photo_id] = back_id_to_correction[back_id]

for k, txt in id_to_text.iteritems():
    id_to_text[k] = cleaner.clean(txt)

back_id_to_text = None  # clear


def image_url(photo_id, is_thumb):
    degrees = id_to_rotation.get(photo_id)
    if not degrees:
        return 'http://oldnyc-assets.nypl.org/%s/%s.jpg' % (
            'thumb' if is_thumb else '600px', photo_id)
    else:
        return 'http://www.oldnyc.org/rotated-assets/%s/%s.%s.jpg' % (
            'thumb' if is_thumb else '600px', photo_id, degrees)


def decode(b):
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
        if title_cleaner.is_pure_location(title):
            original_title = title
            title = ''
        assert r.description() == ''
        assert r.note() == ''

        rotation = id_to_rotation.get(photo_id)
        if rotation and (rotation % 180 == 90):
            w, h = h, w

        response[photo_id] = {
          'title': title,
          'date': re.sub(r'\s+', ' ', r.date()),
          'folder': decode(r.location()),
          'width': w,
          'height': h,
          'text': ocr_text,
          'image_url': image_url(photo_id, is_thumb=False),
          'thumb_url': image_url(photo_id, is_thumb=True)
        }
        if original_title:
            response[photo_id]['original_title'] = original_title
        if rotation:
            response[photo_id]['rotation'] = rotation

    return response


all_photos = []
latlon_to_count = {}
id4_to_latlon = defaultdict(lambda: {})  # first 4 of id -> id -> latlon
for latlon, photo_ids in lat_lon_to_ids.iteritems():
    outfile = '../oldnyc.github.io/by-location/%s.json' % latlon.replace(',', '')
    response = make_response(photo_ids)
    latlon_to_count[latlon] = len(response)
    json.dump(response, open(outfile, 'wb'), indent=2)
    for id_ in photo_ids:
        id4_to_latlon[id_[:4]][id_] = latlon

    for photo_id, response in response.iteritems():
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
          open('../oldnyc.github.io/popular.json', 'wb'), indent=2)

with open('../oldnyc.github.io/lat-lon-counts.js', 'wb') as f:
    f.write('var lat_lons = %s;' % json.dumps(latlon_to_count, indent=2))

for id4, id_to_latlon in id4_to_latlon.iteritems():
    json.dump(id_to_latlon,
              open('../oldnyc.github.io/id4-to-location/%s.json' % id4, 'wb'),
              indent=2)

# Complete data dump
all_photos.sort(key=lambda photo: photo['photo_id'])
json.dump({
            'photos': all_photos,
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'rotation_time': user_rotations['last_date'],
            'ocr_time': manual_ocr_fixes['last_date']
          },
          open('../oldnyc.github.io/data.json', 'wb'),
          indent=2)
