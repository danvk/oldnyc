#!/usr/bin/python
'''Split single image records in the pickle file into multiple records.

Each photo extracted from the original image gets its own record in the new pickle.'''

import os, sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir) 

import cPickle
import copy
import record
import json
from collections import defaultdict

assert len(sys.argv) == 4, 'Usage: %s records.pickle photos.json photos.pickle'
_, in_pickle, photos_json, out_pickle = sys.argv

rs = record.AllRecords(in_pickle)
expansions = json.load(file(photos_json))

f = file(out_pickle, "w")
p = cPickle.Pickler(f, 2)

skipped = 0
num_images, num_photos = 0, 0

for idx, r in enumerate(rs):
  digital_id = r.photo_id()
  image_file = '%s.jpg' % digital_id
  if image_file not in expansions:
    # XXX: why skip any images?
    skipped += 1
    continue
  
  num_images += 1

  if len(expansions[image_file]) == 0:
    r.thumbnail_url = image_file
    r.photo_url = image_file
    p.dump(r)
    num_photos += 1
  else:
    for photo_file in expansions[image_file].keys():
      new_r = copy.deepcopy(r)
      new_id, _  = os.path.splitext(photo_file)
      new_r.tabular['i'] = [new_id]
      new_r.thumbnail_url = photo_file
      new_r.photo_url = photo_file
      p.dump(new_r)
      num_photos += 1

  if num_photos % 1000 == 0:
    sys.stderr.write('Dumped %d images / %d photos\n' % (num_images, num_photos))
  

sys.stderr.write('Skipped %d records\n' % skipped)
