#!/usr/bin/python
#
# The records in records.pickle contain both fields ('title', 'location')
# and a 'tabular' field containing all of this data (tabular['t'],
# tabular['l']). Storing all this data twice is wasteful, and the field
# names clash with accessor methods like Record.title().
#
# This script reads in records.pickle, clears the undesirable fields and
# outputs a new records.pick file.

import cPickle
import record
rs = record.AllRecords()

fields = 0

for r in rs:
  for field in ['title', 'notes', 'description', 'date', 'photo_id', 'location']:
    if field in r.__dict__:
      del r.__dict__[field]
      fields += 1

print 'Deleted %d fields in %d records' % (fields, len(rs))

output_file = "records.clean.pickle"
f = file(output_file, "w")
p = cPickle.Pickler(f, 2)

count = 0
for r in rs:
  p.dump(r)
  count += 1
  if count % 100 == 0:
    print "Pickled %d records" % count
