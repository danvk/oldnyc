#!/usr/bin/python
#
# Run whatever's in the "location" field directly through the geocoder.
# This almost never makes sense for SFPL records, but it does for the
# NYPL Milstein collection.

import fileinput
import re
import sys
import json
import nyc.boroughs

if __name__ == '__main__':
  sys.path += (sys.path[0] + '/..')

import coders.registration
import record


boros = '(?:New York|Manhattan|Brooklyn|Bronx|Queens|Staten Island), (?:NY|N\.Y\.)'
boros_re = r'(New York|Manhattan|Brooklyn|Bronx|Queens|Staten Island), (?:NY|N\.Y\.)$'

streets = '(?:St\.|Street|Place|Pl\.|Road|Rd\.|Avenue|Ave\.|Av\.|Boulevard|Blvd\.|Broadway|Parkway|Pkwy\.|Pky\.|Street \(West\)|Street \(East\))'

# example: "100th Street (East) & 1st Avenue, Manhattan, NY"
# 30337 / 36328 (0.8351)
cross_and_re = r'(.*) (?:&|and|at) (.*), (%s)' % boros

# example: "38th Street (West) - Twelfth Avenue, Manhattan, NY"
#  1616 / 36328 (0.0445)
cross_dash_re = r'([^-,]*?) - ([^-,]*?)(?:[-,].*)?, (%s)' % boros

# example: "York Avenue #1646-50 - 87th Street looking southeast, Manhattan, NY"
#   225
address1_re = r'(.*? %s) #([0-9]+).*(%s)' % (streets, boros)

# example: "929 Park Avenue. Near Eighty-first Street., Manhattan, NY"
#   313
address2_re = r'(\d+)(?:-\d+)? ([a-zA-Z 0-9]*? %s).*, (%s)' % (streets, boros)

cross_patterns = [cross_and_re, cross_dash_re]
addr_patterns = [address1_re, address2_re]

# (From Wikipedia)
staten_neighborhoods = r'Annadale|Arden Heights|Arlington|Arrochar|Bay Terrace|Bloomfield|Brighton Heights|Bulls Head|Castleton|Castleton Corners|Charleston|Chelsea|Clifton|Concord|Dongan Hills|Egbertville|Elm Park|Eltingville|Emerson Hill|Fort Wadsworth|Graniteville|Grant City|Grasmere|Great Kills|Greenridge|Grymes Hill|Hamilton Park|Heartland Village|Huguenot|Lighthouse Hill|Livingston|Manor Heights|Mariners Harbor|Mariner\'s Harbor|Meiers Corners|Midland Beach|New Brighton|New Dorp|New Springville|Oakwood|Ocean Breeze|Old Place|Old Town|Pleasant Plains|Port Richmond|Prince\'s Bay|Randall Manor|Richmond Valley|Richmondtown|Rosebank|Rossville|Sandy Ground|Shore Acres|Silver Lake|South Beach|St\. George|Stapleton|Stapleton Heights|Sunnyside|Todt Hill|Tompkinsville|Tottenville|Tottenville Beach|Travis|Ward Hill|Westerleigh|West New Brighton|Willowbrook|Woodrow'

# def RemoveStatenIslandNeighborhood(addr):
#   if 'Staten Island' in addr:
#     addr = re.sub(staten_neighborhoods_re, ', ', addr)
#   return addr


# Should "Island" be included in this?
place_suffixes = r'Park|Bridge|Campus|College|Station|Church|Square|Hotel|Cemetery|Hospital|Beach|University|Building|Point|H\.S\.|School'

# example: "Empire State Building, Manhattan, N.Y."
# 1083
place_re = r'(.*? (?:%s))\.?, ((?:(?:%s), )?%s)' % (place_suffixes, staten_neighborhoods, boros)

# example: "P.S. 5., Brooklyn, N.Y." (-> Should come out as "PS 123")
# ~150
ps_re = '((?:PS|P\.S\.|Public School) (?:#|No\. )?\d+\.?), ((?:(?:%s), )?%s)' % (staten_neighborhoods, boros)
place_patterns = [place_re, ps_re]

ps_cleanup_re = r'(?:PS|P\.S\.|Public School) (?:#|No\. )?(\d+)\.?'


class MilsteinCoder:
  def __init__(self):
    pass

  def codeRecord(self, r: record.Record):
    # if r.source() != 'Milstein Division': return None

    loc = self._extractLocationStringFromRecord(r)

    m = None
    for pattern in cross_patterns:
      m = re.match(pattern, loc)
      if m: break
    if m:
      crosses = sorted([m.group(1), m.group(2)])
      return {
          'address': '%s and %s, %s' % (crosses[0], crosses[1], m.group(3)),
          'source': loc,
          'type': 'intersection'
      }

    for pattern in addr_patterns:
      m = re.match(pattern, loc)
      if m: break
    if m:
      number, street, city = m.groups()

      # number & street may be swapped.
      try:
        x = int(number)
      except ValueError:
        number, street = street, number

      return {
          'address': '%s %s, %s' % (number, street, city),
          'source': loc,
          'type': 'street_address'
      }

    for pattern in place_patterns:
      m = re.match(pattern, loc)
      if m: break
    if m:
      place, city = m.groups()
      place = re.sub(ps_cleanup_re, r'Public School \1', place)
      return {
          'address': '%s, %s' % (place, city),
          'source': loc,
          'type': 'street_address'  # or 'point_of_interest' or 'establishment'
      }

    sys.stderr.write('(%s) Bad location: %s\n' % (r['id'], loc))
    return None


  def _extractLocationStringFromRecord(self, r: record.Record):
    raw_loc = r['location'].strip()
    loc = re.sub(r'^[ ?\t"\[]+|[ ?\t"\]]+$', '', raw_loc)
    return loc


  def _getLatLonFromGeocode(self, geocode, data):
    for result in geocode['results']:
      # partial matches tend to be inaccurate.
      # if result.get('partial_match'): continue
      # data['type'] is something like 'address' or 'intersection'.
      if data['type'] in result['types']:
        loc = result['geometry']['location']
        return (loc['lat'], loc['lng'])


  def _getBoroughFromAddress(self, address):
    m = re.search(boros_re, address)
    assert m, 'Failed to find borough in "%s"' % address
    record_boro = m.group(1)
    if record_boro == 'New York':
      record_boro = 'Manhattan'
    return record_boro


  def getLatLonFromGeocode(self, geocode, data, r):
    '''Extract (lat, lon) from a Google Maps API response. None = failure.

    This ensures that the geocode is in the correct borough. This helps catch
    errors involving identically-named crosstreets in multiple boroughs.
    '''
    latlon = self._getLatLonFromGeocode(geocode, data)
    if not latlon:
      return None
    lat, lon = latlon

    geocode_boro = nyc.boroughs.PointToBorough(lat, lon)
    record_boro = self._getBoroughFromAddress(data['address'])

    if geocode_boro != record_boro:
      sys.stderr.write('Borough mismatch: "%s" (%s) geocoded to %s\n' % (
          self._extractLocationStringFromRecord(r), record_boro, geocode_boro))
      return None

    return (lat, lon)

  def finalize(self):
    pass

  def name(self):
    return 'milstein'


coders.registration.registerCoderClass(MilsteinCoder)


# For fast iteration
if __name__ == '__main__':
  # XXX this won't work
  coder = MilsteinCoder()
  r = record.Record()
  num_ok, num_bad = 0, 0
  for line in fileinput.input():
    addr = line.strip()
    if not addr: continue
    r.tabular = {
      'i': ['PHOTO_ID'],
      'l': [addr],
      'a': ['Milstein Division']
    }
    result = coder.codeRecord(r)

    print('"%s" -> %s' % (addr, result))
    if result:
      num_ok += 1
    else:
      num_bad += 1

  sys.stderr.write('Parsed %d / %d = %.4f records\n' % (
    num_ok, num_ok + num_bad, 1. * num_ok / (num_ok + num_bad)))
