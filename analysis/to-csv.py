#!/usr/bin/python

import sys
sys.path += (sys.path[0] + '/..')

import csv
import record
rs = record.AllRecords()

csv_writer = csv.writer(open('entries.csv', 'wb'))
csv_writer.writerow(['photo_id', 'date', 'folder', 'title', 'library_url'])

for r in rs:
  date = record.CleanDate(r.date())
  title = record.CleanTitle(r.title())
  folder = record.CleanFolder(r.location())

  csv_writer.writerow([r.photo_id(), date, folder, title, r.preferred_url])
