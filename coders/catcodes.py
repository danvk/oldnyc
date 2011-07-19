#!/usr/bin/python
# Input is a list of "lat,lon : category" lines
#
# Categories are prefixes, i.e. a geocode for "A / B" will apply to "A / B / C".

import record
import re
import coders.locatable
import coders.registration

from collections import defaultdict

class CatCodeCoder:
  def __init__(self):
    self._catmap = {}
    codes = [line.split(" : ") for line in file("cat-codes.txt").read().split("\n") if line]
    assert codes
    for lat_lon, cat in codes:
      lat = float(lat_lon.split(',')[0])
      lon = float(lat_lon.split(',')[1])
      self._catmap[cat] = (lat, lon)

  def codeRecord(self, r):
    cat = record.CleanFolder(r.location())
    if not cat: return None

    for geocat, lat_lon in self._catmap.iteritems():
      if cat.startswith(geocat):
        return coders.locatable.fromLatLon(lat_lon[0], lat_lon[1],
                                           source='Folder: ' + geocat)

    return None

  def name(self):
    return 'catcodes'


coders.registration.registerCoderClass(CatCodeCoder)
