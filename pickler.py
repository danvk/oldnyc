#!/usr/bin/python
#
# Pickles the entire collection of digital photo records.
# This should make reading them back significantly faster.

import cPickle
import glob
import record

output_file = "records.pickle"
f = file(output_file, "w")
p = cPickle.Pickler(f, 2)

count = 0
missing_count = 0

for filename in glob.glob("records/*"):
  count += 1
  r = record.Record.FromString(file(filename).read())
  if not r:
    missing_count += 1
    continue

  p.dump(r)
  if count % 100 == 0:
    print "Pickled %d records" % count
