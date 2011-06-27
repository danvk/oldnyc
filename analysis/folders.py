#!/usr/bin/python
import record
rs = record.AllRecords()

for r in rs:
  if r.location():
    print r.location()
  else:
    print '(none)'
