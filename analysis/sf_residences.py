#!/usr/bin/python
#
# Look at folders like "S.F. Residences / 141 Brompton Avenue"
# If there are numbers, then it's almost certainly an address.

import sys
sys.path += (sys.path[0] + '/..')

import re
import record
import cPickle

output_mode = 'pickle'
outputs = []

rs = record.AllRecords()

for r in rs:
  loc = r.location()
  if not loc.startswith('Folder: S.F. Residences'): continue

  # The simple version screws up folders like 'S.F. Residences-710-720 Steiner'
  parts = loc.split("-")
  maybe_address = parts[1]
  n = 2
  while re.match(r' *\d+ *', maybe_address) and n < len(parts):
    maybe_address += '-' + parts[n]
    n += 1

  maybe_address = re.sub(r' ?\(.*\)', '', maybe_address)
  if maybe_address[-1] == '.': maybe_address = maybe_address[:-1]

  if not re.search(r'\d', maybe_address): continue

  # Hyphenated addresses are too hard. We punt and take the first one.
  # ex: 434-40 Presidio Avenue -> 434 Presidio Avenue
  # ex: 2614-16-18-20 Buchanan -> 2614 Buchanan
  if '-' in maybe_address:
    maybe_address = re.sub(r'(-\d+)+', '', maybe_address)

  # Special cases:
  # o Google maps wants 'California Street', not 'California'
  # o The library has a typo in entries AAC-5953 and AAC-5954
  maybe_address = re.sub('California$', 'California Street', maybe_address)
  if maybe_address == '33343 Pacific':
    maybe_address = '3343 Pacific Avenue'

  if output_mode == 'text':
    print '%s\t%s' % (r.photo_id(), maybe_address)
  elif output_mode == 'pickle':
    outputs.append([r.photo_id(), None, ['address:' + maybe_address]])

if output_mode == 'pickle':
  print 'Outputting %d residence addresses' % len(outputs)
  cPickle.dump(outputs, file('/tmp/sf-residences.pickle', 'w'))
