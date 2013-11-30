"""Utility for mapping a lat/lon to a borough."""

import json
import shape_utils
import re

boroughs = None

def PointToBorough(lat, lon):
  global boroughs
  if not boroughs:
    boroughs = json.load(file('borough-polygons.json'))

  pt = (lon, lat)
  for k, v in boroughs.iteritems():
    if shape_utils.PointInPolygon(pt, v):
      return k
  return None


if __name__ == '__main__':
    re.match()
