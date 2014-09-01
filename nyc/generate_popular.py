#!/usr/bin/env python
'''Generates popular-photos.js.

Data source is https://docs.google.com/spreadsheet/ccc?key=0Anx1yCqeL8YUdHE0dXR6R01TVnFOeWNkaWpTTHpta2c&usp=docslist_api#gid=2
'''

import csv
import sys
import json

def run():
    assert len(sys.argv) == 2

    photos = []
    id_to_photo = {}
    for row in csv.DictReader(open(sys.argv[1])):
        if row['Image ID'] == '':
            break
        photo = {
            'id': row['Image ID'],
            'date': row['Date'],
            'loc': row['Location'],
            'desc': row['Description']
        }
        photos.append(photo)
        id_to_photo[photo['id']] = photo

    sys.stderr.write('Loaded %d popular images\n' % len(photos))

    for row in csv.reader(open('nyc-image-sizes.txt')):
        photo_id, width, height = row
        width = int(width)
        height = int(height)
        try:
            id_to_photo[photo_id]['height'] = int(round(200. * height/width))
        except KeyError:
            pass

    for row in photos:
        assert 'height' in row

    open('viewer/static/js/popular-photos.js', 'w').write(
            'var popular_photos = %s;\n' % json.dumps(photos))

if __name__ == '__main__':
    run()
