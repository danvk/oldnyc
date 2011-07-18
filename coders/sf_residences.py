#!/usr/bin/python
#
# Look at folders like "S.F. Residences / 141 Brompton Avenue"
# If there are numbers, then it's almost certainly an address.

import record
import re
import coders.locatable
import coders.registration


class ResidencesCoder:
  def __init__(self):
    pass

  def codeRecord(self, r):
    loc = r.location()
    if not loc.startswith('Folder: S.F. Residences'): return None

    # The simple version screws up folders like 'S.F. Residences-710-720 Steiner'
    parts = loc.split("-")
    maybe_address = parts[1]
    n = 2
    while re.match(r' *\d+ *', maybe_address) and n < len(parts):
      maybe_address += '-' + parts[n]
      n += 1

    maybe_address = re.sub(r' ?\(.*\)', '', maybe_address)
    if maybe_address[-1] == '.': maybe_address = maybe_address[:-1]

    if not re.search(r'\d', maybe_address): return None

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

    maybe_address = maybe_address.strip()
    return coders.locatable.fromAddress(maybe_address, source=maybe_address)


  def name(self):
    return 'SF Residences'


coders.registration.registerCoderClass(ResidencesCoder)
