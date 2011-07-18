#!/usr/bin/python
#
# This class represents some sort of locatable information:
#
#   o Latitude and Longitude
#   o An address
#   o A city block (e.g. '2500 block of Valencia')
#   o A short street
#   o Cross streets (e.g. Valencia and Market)
#   o A set of cross streets (e.g. Market between 4th and 5th)

LAT_LON = 0
ADDRESS = 1
TINY = 2
CROSSES = 3
BLOCK = 4

class Locatable(object):
  def __init__(self):
    self.loc_type = None
    self.lat = None
    self.lon = None
    self.address = None
    self.tiny = None
    self.crosses = None
    self.source = None

  def __str__(self):
    if not self.source: return ''
    return self.source


def fromLatLon(lat, lon, source=None):
  l = Locatable()
  l.loc_type = LAT_LON
  l.lat = lat
  l.lon = lon
  if source:
    l.source = source
  else:
    l.source = '@' + lat + ',' + lon
  return l


def fromAddress(address, source=None):
  l = Locatable()
  l.loc_type = ADDRESS
  l.address = address
  if source:
    l.source = source
  else:
    l.source = address
  return l


def fromBlock(block, street, source=None):
  l = Locatable()
  l.loc_type = BLOCK
  l.block_num = block
  l.street = street
  if source:
    l.source = source
  else:
    l.source = '%d block of %s' % (l.block_num, l.street)
  return l


def fromTiny(tiny, source=None):
  l = Locatable()
  l.loc_type = TINY
  l.tiny = tiny
  if source:
    l.source = source
  else:
    l.source = tiny
  return l


def fromCross(street1, street2, source=None):
  l = Locatable()
  l.loc_type = CROSSES
  l.crosses = [ sorted([street1, street2]) ]
  if source:
    l.source = source
  else:
    l.source = '%s and %s' (street1, street2)
  return l


def fromStreetAndCrosses(street1, crosses, source=None):
  l = Locatable()
  l.loc_type = CROSSES
  l.crosses = [ sorted([street1, street2]) for street2 in crosses]
  if source:
    l.source = source
  else:
    if len(crosses) == 1:
      l.source = '%s and %s' % (street1, crosses[0])
    else:
      l.source = '%s and [%s]' % (street1, ', '.join(crosses))
  return l


def fromCrosses(crosses, source=None):
  l = Locatable()
  l.loc_type = CROSSES
  l.crosses = [ sorted([s1, s2]) for s1, s2 in crosses ]
  if source:
    l.source = source
  else:
    l.source = ', '.join(['%s and %s' % (a,b) for a,b in crosses])
  return l
