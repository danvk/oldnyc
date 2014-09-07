#!/usr/bin/env python
'''Serve OldNYC using local assets.'''

import csv
import json
from Flask import Response, current_app

import devserver
import record

rs = record.AllRecords('nyc/photos.pickle')
id_to_record = {r.photo_id(): r for r in rs}

id_to_dims = {}
for photo_id, width, height in csv.reader(open('nyc-image-sizes.txt')):
    id_to_dims[photo_id] = (width, height)


def RootHandler(path, request):
    return current_app().send_static_file('static/viewer.html')


def RecordFetcher(path, request):
    pass


if __name__ == '__main__':
    devserver.make_app('viewer/app.yaml', [
        ('/', RootHandler),
        ('/info', RecordFetcher),
    ]).run(host='0.0.0.0', debug=True)
