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

import math
import sys
import geocoder

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
    self.block_num = None
    self.block_street = None
    self._latlon = 'unknown'

  def __str__(self):
    if not self.source: return ''
    return self.source

  def getLatLon(self, g=None):
    """Returns either a (lat, lon) tuple or None."""
    if self._latlon != 'unknown': return self._latlon
    if self.loc_type == LAT_LON:
      self._latlon = (self.lat, self.lon)
    elif self.loc_type == ADDRESS:
      self._latlon = locateAddress(g, self.address)
    elif self.loc_type == BLOCK:
      self._latlon = locateBlock(g, self.block_num, self.block_street)
    elif self.loc_type == TINY:
      self._latlon = locateTiny(g, self.tiny)
    elif self.loc_type == CROSSES:
      self._latlon = locateCrosses(g, self.crosses)
    else:
      assert False, 'Unknown loc_type %d' % self.loc_type
    return self._latlon


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
  assert 0 == block % 100, 'Block not divisible by 100! %s' % source
  l = Locatable()
  l.loc_type = BLOCK
  l.block_num = block
  l.block_street = street
  if source:
    l.source = source
  else:
    l.source = '%d block of %s' % (l.block_num, l.block_street)
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
    l.source = '%s and %s' % (street1, street2)
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


# Geolocation


def GetAverageLatLon(lat_lons):
  # compute all-pairs distances. They should all be tightly clustered, say
  # within half a mile. For reference, Folsom&4th to Folsom&5th is 0.17 miles.
  ds = []
  for i in range(len(lat_lons)):
    for j in range(i + 1, len(lat_lons)):
      ds.append(LatLonDistance(lat_lons[i][0], lat_lons[i][1], lat_lons[j][0], lat_lons[j][1]))

  d = max(ds)
  if d > 0.5: return None

  lat = 0.0
  lon = 0.0
  for xlat, xlon in lat_lons:
    lat += xlat
    lon += xlon
  lat /= len(lat_lons)
  lon /= len(lat_lons)
  return (lat, lon)


def InSF(lat, lon):
  if lat < 37.684907 or lon < -122.517471:  # sw -- in the ocean south of the zoo
    return False
  if lat > 37.833649 or lon > -122.35817:  # ne -- just off the edge of Treasure Island
    return False
  return True


def InNYC(lat, lon):
  return (40.486649 < lat < 40.921814 and
         -74.288864 < lon < -73.689423)


def Locate(g, addr):
  x = g.Locate(addr)
  if x.status != 200:
    sys.stderr.write("%s -> status %d\n" % (addr, x.status))
    return None
  if not InSF(x.lat, x.lon) and not InNYC(x.lat, x.lon): return None
  return x


def LatLonDistance(lat1, lon1, lat2, lon2):
  """The "haversine" formula."""
  R = 3963  # mi
  dLat = (lat2-lat1) * math.pi / 180.0
  dLon = (lon2-lon1) * math.pi / 180.0
  lat1 = lat1 * math.pi / 180.0
  lat2 = lat2 * math.pi / 180.0

  a = math.sin(dLat/2) * math.sin(dLat/2) + \
      math.sin(dLon/2) * math.sin(dLon/2) * math.cos(lat1) * math.cos(lat2);
  c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a));
  d = R * c
  return d


def locateAddress(g, address):
  x = Locate(g, address)
  if not x or x.accuracy != 8:
    sys.stderr.write('Failure: %s -> %s\n' % (address, x))
    return None
  return (x.lat, x.lon)


def locateBlock(g, block_num, block_street):
  loc_str = str(block_num + 50) + ' ' + block_street
  x = Locate(g, loc_str)
  if not x or x.accuracy != 8:
    sys.stderr.write('Failure: %s -> %s\n' % (loc_str, x))
    return None
  else:
    return (x.lat, x.lon)


def locateTiny(g, tiny):
  loc = tiny
  if not ' ' in loc: loc += ' street'
  x = Locate(g, loc)
  if not x or x.accuracy != 6:
    sys.stderr.write('Failure: %s -> %s\n' % (loc, x))
    return None
  else:
    return (x.lat, x.lon)


# These intersections/streets have changed names since the photos were taken.
fixes = {
  '13th and howard': '13th and south van ness',
  '14th and howard': '14th and south van ness',
  '15th and howard': '15th and south van ness',
  '16th and howard': '16th and south van ness',
  '17th and howard': '17th and south van ness',
  '18th and howard': '18th and south van ness',
  'eighteenth and howard': '18th and south van ness',
  '19th and howard': '19th and south van ness',
  '20th and howard': '20th and south van ness',
  '21st and howard': '21st and south van ness',
  '22nd and howard': '22nd and south van ness',
  '23rd and howard': '23rd and south van ness',
  '24th and howard': '24th and south van ness',
  '25th and howard': '25th and south van ness',

  'castro and market': 'castro street and market street',  # this is strange!
  'california and market': 'spear street and market street',
  'market and post': '2nd street and market street',
  'embarcadero and market': 'Harry Bridges Plaza',
  'sloat and sunset': '@37.733865,-122.493889',
  'eddy and market': '@37.784724,-122.407715',
  'eddy and powell': '@37.784724,-122.407715',

  '15th and bryant street': '@37.767102,-122.412565'
}

def locateCrosses(g, crosses):
  global fixes
  lat_lons = []
  loc_strs = []
  for pair in crosses:
    street1, street2 = pair
    locatable = ' and '.join(pair)
    # a few special cases for streets that were renamed or intersections that
    # no longer exist.
    take_it = False
    if locatable in fixes:
      locatable = fixes[locatable]
      if 'and' not in locatable: take_it = True

    locatable = locatable.replace('army', 'cesar chavez')
    if locatable[0] != '@':
      x = Locate(g, locatable)
    else:
      ll = locatable[1:].split(',')
      x = geocoder.FakeLocation(float(ll[0]), float(ll[1]), 7)

    if not x or (x.accuracy != 7 and not take_it):
      sys.stderr.write('Failure: %s -> %s\n' % (locatable, x))
    else:
      lat_lons.append((x.lat, x.lon))
      loc_strs.append(locatable)

  if len(lat_lons) == 1:
    return (lat_lons[0][0], lat_lons[0][1])
  elif len(lat_lons) > 0:
    # TODO(danvk): check for important strings like "between"
    return GetAverageLatLon(lat_lons)
  # these are geocode failures
  return None
