#!/usr/bin/python
#
# Expand locations for individual records to their entire folders. This doesn't
# always work, so we wind up using a manually-generated whitelist.
#
# The manual filtering and whitelist generation is done via
# analysis/generalize.py.

import record
import coders.locatable
import coders.registration

class GeneralizationCoder:
  def __init__(self):
    lines = file('generalized-locations.txt').read().split('\n')
    self._id_map = {}  # photo_id -> (latlon, source)
    for line in lines:
      if not line: continue
      photo_id, latlon, source = line.split('\t')
      self._id_map[photo_id] = (latlon, source)


  def codeRecord(self, r):
    if r.photo_id() not in self._id_map: return None

    latlon, source = self._id_map[r.photo_id()]
    lat = float(latlon.split(',')[0])
    lon = float(latlon.split(',')[1])
    return coders.locatable.fromLatLon(lat, lon, source=source)


  def name(self):
    return 'generalization'


coders.registration.registerCoderClass(GeneralizationCoder)
