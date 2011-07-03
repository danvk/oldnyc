#!/usr/bin/python

import sys
sys.path += (sys.path[0] + '/..')

import re
import record
rs = record.AllRecords()

for r in rs:
  if r.location():
    # remove leading 'Folder: ', trailing period & convert various forms of
    # dashes to a single form of slashes.
    folder = r.location()
    if folder:
      if folder[-1] == '.' and not folder[-3] == '.':  # e.g. 'Y.M.C.A'
        folder = folder[:-1]
      folder = folder.replace('Folder: ', '')
      folder = re.sub(r' *- *', ' / ', folder)

    # remove [graphic] from titles
    title = r.title().replace(' [graphic].', '')
    title = title.replace('[', '').replace(']','')

    # remove [] and trailing period from dates.
    date = r.date().replace('[', '').replace(']','')
    if date[-1] == '.': date = date[:-1]

    print '\t'.join([folder, date, title, r.preferred_url])
  else:
    print '(none)'
