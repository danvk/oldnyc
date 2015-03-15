#!/usr/bin/env python
'''Generate a static version of oldnyc.org consisting entirely of JSON.'''

import chardet
import csv
import json
import record
import re

# strip leading 'var lat_lons = ' and trailing ';'
lat_lon_to_ids = json.loads(open('viewer/static/js/nyc-lat-lons-ny.js', 'rb').read()[15:-1])

rs = record.AllRecords('nyc/photos.pickle')
id_to_record = {r.photo_id(): r for r in rs}

id_to_dims = {}
for photo_id, width, height in csv.reader(open('nyc-image-sizes.txt')):
    id_to_dims[photo_id] = (width, height)

# ocr.json maps "12345b" -> text. We need photo id -> text.
back_id_to_text = json.load(open('ocr/ocr.json', 'rb'))
id_to_text = {}
for photo_id in id_to_record.iterkeys():
    back_id = 'book' + re.sub(r'f?(?:-[a-z])?$', 'b', photo_id)
    if back_id in back_id_to_text:
        id_to_text[photo_id] = back_id_to_text[back_id]
back_id_to_text = None  # clear


def decode(b):
    try:
        return b.decode('utf8')
    except UnicodeDecodeError:
        return b.decode(chardet.detect(b)['encoding'])

latlon_to_count = {}
for latlon, photo_ids in lat_lon_to_ids.iteritems():
    outfile = '../oldnyc.github.io/by-location/%s.json' % latlon.replace(',', '')
    response = {}
    for photo_id in photo_ids:
        r = id_to_record[photo_id]
        w, h = id_to_dims[photo_id]
        ocr_text = id_to_text.get(photo_id)

        # copied from viewer/app.py
        title = r.title()
        if r.description():
          title += '; ' + r.description()
        if r.note():
          title += '; ' + r.note()
        response[photo_id] = {
          'title': decode(title),
          'date': re.sub(r'\s+', ' ', r.date()),
          'folder': decode(r.location()),
          'width': w,
          'height': h,
          'text': ocr_text
        }

    latlon_to_count[latlon] = len(response)
    json.dump(response, open(outfile, 'wb'), indent=2)

with open('../oldnyc.github.io/lat-lon-counts.js', 'wb') as f:
    f.write('var lat_lons = %s;' % json.dumps(latlon_to_count, indent=2))
