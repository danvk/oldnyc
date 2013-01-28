#!/usr/bin/python
#
# Converts the milstein.csv file to a pickle file of Record objects.
# NOTE! Should be run from the nyc directory.

import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir) 

import cPickle
import record
import csv

output_file = "records.pickle"
f = file(output_file, "w")
p = cPickle.Pickler(f, 2)

reader = csv.DictReader(file('milstein.csv'))
for idx, row in enumerate(reader):
  url = row['IMAGE_Permalink'].strip()
  assert url

  img_url = row['IMG_URL'].strip()
  assert img_url

  photo_id = row['DIGITAL_ID'].strip()
  assert photo_id

  date_str = row['CREATED_DATE'].strip()
  # date_str is not always present

  full_address = row['Full Address'].strip()
  creator = row['CREATOR'].strip()

  title = row['IMAGE_TITLE'].strip()
  assert title

  # TODO(danvk): move this into record.py
  r = record.Record()
  r.thumbnail_url = img_url  # TODO(danvk): real thumbnail
  r.photo_url = img_url
  r.preferred_url = url
  r.tabular = {
    'l': [full_address],  # NOTE: "Location" = folder for SFPL, not address
    'i': [photo_id],
    'p': [date_str],
    'r': [''],  # description
    't': [title],
    'n': [''],  # notes
    'a': ['Milstein Division']
  }
  p.dump(r)

  count = 1 + idx
  if count % 100 == 0:
    print "Pickled %d records" % count
