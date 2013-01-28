#!/usr/bin/python
# This reads dates from stdin/files and attempts to parse them into
# [earliest possible, latest possible] ranges.
#
# It outputs YYYY-MM-DD\tYYYY-MM-DD lines.

import record
import fileinput

for line in fileinput.input():
  line = line.strip()
  r = record.Record.ExtractDateRange(line)
  if r:
    txts = []
    for d in r:
      txt = ''
      if d:
        # note: datetime.strftime only works for years >= 1900.
        txt = '%04d-%02d-%02d' % (d.year, d.month, d.day)
      else:
        txt = '????-??-??'
      txts.append(txt)
    txts.append(line)
    print '\t'.join(txts)
