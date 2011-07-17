#!/usr/bin/python
#
# Look for addresses and sets of cross-streets in the free-standing "title"
# text. This text isn't structured in the way that the "S.F. Streets" folders
# are, so we have to be more cautious about what we match. This is done via a
# whitelist of regular expressions.

import sys
sys.path += (sys.path[0] + '/..')

import re
import record
import cPickle
import sf_streets
from collections import defaultdict

rs = record.AllRecords()

street_list = file("street-list.txt").read().split("\n")
street_list = [s.lower() for s in street_list if s]

street_re = '(?:' + '|'.join(street_list) + ')'
addr_re = r'[-0-9]{2,} +' + street_re + r' +(street|st|avenue|ave|road|boulevard|blvd|place|way|bus|line|express bus|area|rush)?'

# There's some overlap here, but they're in decreasing order of confidence.
# More confident (i.e. longer) forms get matched first.
forms = [
  '(' + street_re + '(?: +street|st\.)?),? +between +(' + street_re + ' (?:street )?)(?:and|&) +(' + street_re + r')\b',  # A between B and C (47; sparse, but "protects" the next forms)
  '(' + street_re + ') +(?:and|&) +(' + street_re + ' +street)s',         # A and B streets (1027 records)
  '(' + street_re + ') +(?:and|&) +(' + street_re + ' +st)s',             # A and B sts (46 records)
  '(' + street_re + ') +(?:and|&) +(' + street_re + r' +(street|st|ave|avenue))\b',  # A and B st/street (193)
  '(' + street_re + ') +& +(' + street_re + r'\b)',  # A & B (106)
  '(?:at|of) (' + street_re + ') +and +(' + street_re + r'\b)',  # at A and B (104)

  # Rejected forms:
  # street_re + ',? (north|south|east|west) of ' + street_re + r'\b', (only 6)
  # street_re + ' +and +' + street_re,  # A and B (235 but w/ lots of false positives)
]
forms = [re.compile(form) for form in forms]

# Some things look like addresses (e.g. '1939 Golden Gate Expo', '38 Geary bus
# line') but are not.
def should_reject_address(addr):
  if re.search(r'\b(bus|line)\b', addr): return True
  if '1939 golden gate' in addr: return True
  if '1940 golden gate' in addr: return True
  if 'bay area' in addr: return True
  if 'gold rush' in addr: return True
  if '214 carl' in addr: return True
  m = re.search(r'^(\d+)', addr)
  if not m: return True
  address_no = int(m.group(0))
  if address_no == 0: return True
  if address_no < 10: return True
  return False


if __name__ == '__main__':
  outputs = []
  stats = defaultdict(int)
  for r in rs:
    # SF Streets are handled elsewhere
    if r.location().startswith("Folder: S.F. Streets-"): continue
    if r.location().startswith('Folder: S.F. Earthquakes-1906-Streets'): continue
    if r.location().startswith('Sheet: S.F. Streets'): continue

    # this is too strong -- sometimes it's something like 'Spreckels Mansion' and
    # there's a more useful address in the description.
    if r.location().startswith('Folder: S.F. Residences'): continue

    title = sf_streets.clean_street(record.CleanTitle(r.title()).lower())

    # look for an exact address
    m = re.search(addr_re, title)
    if m:
      # filter out '38 geary bus', '22 fillmore line', '12 ocean  line'
      addr = m.group(0)
      if not should_reject_address(addr):
        print 'a\t%s\t%s\t%s' % (r.photo_id(), m.group(0), title)
        stats['a'] += 1
        outputs.append([r.photo_id(), None, [ 'address:' + addr ]])
        continue

    # Common cross-street patterns
    for idx, pat in enumerate(forms):
      m = re.search(pat, title)
      if m:
        print '%d\t%s\t%s\t%s' % (1 + idx, r.photo_id(), m.group(1) + ' and ' + m.group(2), title)
        stats[str(1 + idx)] += 1
        if idx == 0:
          pass  # TODO(danvk): handle "A between B and C"
        else:
          outputs.append([r.photo_id(), m.group(1), [ m.group(2) ]])
        break

  tally = 0
  for k in sorted(stats.keys()):
    sys.stderr.write('%5d %s\n' % (stats[k], k))
    tally += stats[k]
  sys.stderr.write('%5d total\n' % tally)

  if outputs:
    cPickle.dump(outputs, file('/tmp/sf-freestanding.pickle', 'w'))
