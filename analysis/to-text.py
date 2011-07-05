#!/usr/bin/python

import sys
sys.path += (sys.path[0] + '/..')

import record
rs = record.AllRecords()

for r in rs:
  date = record.CleanDate(r.date())
  title = record.CleanTitle(r.title())
  folder = r.location()
  if folder: folder = record.CleanFolder(folder)

  print '\t'.join([r.photo_id(), date, folder, title, r.preferred_url])
