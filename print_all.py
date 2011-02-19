#!/usr/bin/python
import record
import glob
import sys
from datetime import date

rs = record.AllRecords()

def Bump(d, k, v=1):
  d[k] = v + d.setdefault(k, 0)

missing_count = 0
count = 0
streets = 0
starts = {}
ends = {}
tags = {}
for r in rs:
  count += 1
  for tag in r.tabular.keys():
    Bump(tags, tag)

print "Tags:"
for tag in sorted(tags.keys()):
  print "  %s: %d" % (tag, tags[tag])

  # if r.location and 'Folder: S.F. Streets' in r.location:
  #   streets += 1

  #start, end = r.date_range()
  #if start: Bump(starts, start.year)
  #if end: Bump(ends, end.year)
  #if end and end <= date(1856, 1, 1):
  #  print "%s %s" % (end, r.preferred_url)

#all_years = set(starts.keys()) | set(ends.keys())
#for year in sorted(all_years):
#  print "%d\t%d\t%d" % (year, starts.get(year, 0), ends.get(year, 0))

# print "Tags:"
# tags = record.Record.TagIds()
# for k in sorted(tags.keys()):
#   print "%s:" % k
#   names = []
#   for (name, v) in tags[k].iteritems():
#     names.append((v, name))
#   for (v, name) in reversed(sorted(names)):
#     print "  %6d %s" % (v, name)
