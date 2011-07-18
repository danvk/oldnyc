#!/usr/bin/python

import record
import re
import coders.locatable
import coders.registration
import coders.sf_streets

from collections import defaultdict

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


class FreeStreetCoder:
  def __init__(self):
    street_list = file("street-list.txt").read().split("\n")
    street_list = [s.lower() for s in street_list if s]

    street_re = '(?:' + '|'.join(street_list) + ')'
    self._addr_re = r'[-0-9]{2,} +' + street_re + r' +(street|st|avenue|ave|road|boulevard|blvd|place|way|bus|line|express bus|area|rush)?'

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
    self._forms = [re.compile(form) for form in forms]
    self._stats = defaultdict(int)

  def codeRecord(self, r):
    title = coders.sf_streets.clean_street(record.CleanTitle(r.title()).lower())

    # look for an exact address
    m = re.search(self._addr_re, title)
    if m:
      addr = m.group(0)
      if not should_reject_address(addr):
        return coders.locatable.fromAddress(addr)

    # Common cross-street patterns
    for idx, pat in enumerate(self._forms):
      m = re.search(pat, title)
      if m:
        self._stats[str(1 + idx)] += 1
        if idx != 0:
          return coders.locatable.fromCross(m.group(1), m.group(2),
                                            source=m.group(0))
        else:
          return coders.locatable.fromStreetAndCrosses(
              m.group(1), [m.group(2), m.group(3)])

    # No dice.
    return None


  def name(self):
    return 'free-streets'


coders.registration.registerCoderClass(FreeStreetCoder)
