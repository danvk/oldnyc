#!/usr/bin/python
#
# Upload records which are complete to app engine.
#
# Usage:
# ./upload_to_appengine.py records.pickle lat-lons.js [upload url]

# TODO(danvk): upload >1 record per request

import random
import re
import record
import fetcher
import sys
import httplib
import MultipartPostHandler, urllib2, urllib
import json
from optparse import OptionParser


CHUNK_SIZE = 100  # number of records to set per HTTP POST

parser = OptionParser()
parser.add_option('', '--pickle_path', default=None, dest='pickle_path',
                  help='Point to a records.pickle file.')
parser.add_option('', '--lat_lons_js_path', default=None,
                  dest='lat_lons_js_path',
                  help='Point to a lat-lons.js file. Used as a filter.')
parser.add_option('', '--image_sizes_path', default='', dest='image_sizes_path',
                  help='Path to a file of images sizes, as output by ' +
                  'extract-sizes.py.')
parser.add_option('', '--upload_url', dest='upload_url',
                  default='http://localhost:8080/upload',
                  help='Upload endpoint. Default is local dev_appserver.')
parser.add_option('', '--start_chunk', default=0, dest='start_chunk', type=int,
                  help='Which chunk to start with. Used to resume uploads.')

(options, args) = parser.parse_args()

assert options.pickle_path
assert options.image_sizes_path


all_rs = record.AllRecords(options.pickle_path)

# The JS file has a leading 'var foo = {' and a trailing '};' that we don't want.
lat_lons = {}
if options.lat_lons_js_path:
  js_data = file(options.lat_lons_js_path).readlines()
  js_data = '{'+ ''.join(js_data[1:-1]) + '}'
  lat_lons = json.loads(js_data)

  ok_ids = set()
  for ll, images in lat_lons.iteritems():
    for _, _, photo_id in images:
      ok_ids.add(photo_id)

  rs = [r for r in all_rs if r.photo_id() in ok_ids]
else:
  rs = all_rs

id_to_dims = {}
for line in file(options.image_sizes_path):
  image_id, width, height = line.strip().split(',')
  id_to_dims[image_id] = (width, height)

for r in rs:
  assert r.photo_id() in id_to_dims, 'Missing dimensions for %s' % r.photo_id()

sys.stderr.write('Have %d full records\n' % len(rs))

print 'Will upload via %s' % options.upload_url


opener = urllib2.build_opener(MultipartPostHandler.MultipartPostHandler)


# via http://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks-in-python
def chunks(l, n):
  '''Yield successive n-sized chunks from l.'''
  for i in xrange(0, len(l), n):
    yield l[i:i+n]


for i, chunk_rs in enumerate(chunks(rs, CHUNK_SIZE)):
  if i < options.start_chunk:
    continue

  print 'Chunk %d of %d' % (i, int(len(rs)/CHUNK_SIZE))

  vals = []
  for r in chunk_rs:
    # Misc late-stage cleanup:
    # Delete non-helpful "descriptions"
    desc = r.description()
    if re.match(r'^1 photographic print *: *color\.?$', desc) or \
        re.match(r'^1 photographic print *: *b&w\.?$', desc):
      desc = ''

    # remove [] and trailing period from dates.
    date = record.CleanDate(r.date())

    # remove [graphic] from titles
    title = record.CleanTitle(r.title())

    # remove leading 'Folder: ', trailing period & convert various forms of
    # dashes to a single form of slashes.
    folder = r.location()
    if folder: folder = record.CleanFolder(folder)

    width, height = id_to_dims[r.photo_id()]

    try:
      q = {
        'photo_id': r.photo_id(),
        'title': title.replace('\n', ' ')[:200],
        'date': date,
        'folder': folder.replace('\n', ' '),
        'description': desc,
        'note': (r.note() or ''),
        'library_url': r.preferred_url,
        'width': width,
        'height': height
      }
      vals.append(json.dumps(q))
    except UnicodeDecodeError as e:
      sys.stderr.write('Unicode error with photo %s\n' % r.photo_id())

  q_pairs = [('r', val) for val in vals]
  opener.open(options.upload_url, urllib.urlencode(q_pairs))

# To clear the data store, run:
# import db
# qs = db.ImageRecord.all()
# for q in qs: q.delete()
