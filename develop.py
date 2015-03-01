#!/usr/bin/env python
'''Serve OldNYC using local assets.'''

import csv
import json
import re
import sys

from flask import Response, current_app, jsonify

import devserver
import record

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

print 'Loaded OCR for %d photo ids' % len(id_to_text)


def RootHandler(path, request):
    return current_app.send_static_file('static/viewer.html')


def RecordFetcher(path, request):
    response = {}
    photo_ids = request.form.getlist('id')
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
          'title': title,
          'date': r.date(),
          'folder': r.location(),
          'width': w,
          'height': h,
          'text': ocr_text
        }

    return jsonify(response)


def RecordFeedback(path, request):
    form = request.form
    print 'Feedback: (%s) %s' % (form.get('id'), form.get('feedback'))
    return "OK"


if __name__ == '__main__':
    try:
        port = int(sys.argv[1])
    except IndexError:
        port = 5000

    devserver.make_app('viewer/app.yaml', [
        ('/', RootHandler),
        ('/info', RecordFetcher),
        ('/rec_feedback', RecordFeedback),
    ]).run(host='0.0.0.0', port=port, debug=True)  # set debug=True if you want to iterate on Python, not static content.
