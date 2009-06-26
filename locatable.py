# Basic idea of this method is to guess whether a record will be successfully
# located using the Google Maps API's Geocoder. Looks for text that appears to
# be an address or cross streets.
import re
import record

# Useful folder: "Folder: S.F. Residences-2700 California."

by_address = 0
by_and_cross = 0
by_street_cross = 0
by_pier = 0
by_at_cross = 0
failure = 0
total = 0
from_title = 0
from_location = 0
maybe_year = 0
buildings = {
'Ferry Building': 0,
'Civic Center': 0,
'Palace Hotel': 0
}

def IsLocatable(r):
  """Return true if the record is likely to be successfully geocoded."""
  global failure, total, from_title, from_location
  total += 1
  if '' == r.title(): return None

  return LocationSubstring(r.title())


def LocationSubstring(str):
  global by_address, by_and_cross, by_street_cross, by_pier, by_at_cross
  global maybe_year
  # Match something like "908 Steiner" or "123 45th Ave"
  # TODO(danvk): find the shortest substring starting with digits and ending
  # with "St.", "Street", "Ave", "Avenue", "Blvd.", etc.
  # TODO(danvk): email the geocoding people about free text geocoding.
  street_like = r'(?:(?:[A-Z][a-z]|[1-9]+[snrt]).+?\b)'
  m = re.search(r'[\[ ]((\d\d+) %s)\b' % street_like, str)
  if m:
    by_address += 1
    if m.group(2) >= '1900' and m.group(2) < '2000':
      maybe_year += 1
    #print "Address '%s' (%s)" % (m.group(1), str)
    return m.group(1)

  return None

  m = re.search(r'(?i)\bPier \d+', str)
  if m:
    by_pier += 1
    # TODO(danvk): geocode these directly
    #print "Pier (%s)" % str
    return True

  # TODO:
  # - Libraries
  # - Bridges
  # - Schools
  # - Theaters
  # - Civic Center and Mint
  # - Churches
  # - Parks

  if re.search(r'(?i)streets(?!-)(?! -)', str):
    by_street_cross += 1
    #print "SCross? (%s)" % str
    return True

  global buildings
  for k in buildings.iterkeys():
    if re.search(k, str, re.IGNORECASE):
      #print "Building (%s)" % str
      buildings[k] += 1
      return True

  if (re.search(r' [aA]t %s' % street_like, str) and
      re.search(r'(?i)\b(?:street|ave|blvd|boulevard)', str)):
    by_at_cross += 1
    #print "@Cross? (%s)" % str
    return True

  if (re.search(r' [aA]nd (?!Mr|Mrs|Dr|Miss)%s' % street_like, str) and
      re.search(r'(?i)\b(?:street|ave|blvd|boulevard)', str)):
    by_and_cross += 1
    #print "ACross? (%s)" % str
    return True

  return False

def PrintLocationStats():
  print "Address: %0.2f (%d/%d)" % (100.0 * by_address/total, by_address, total)
  print "Pier: %0.2f (%d/%d)" % (100.0 * by_pier/total, by_pier, total)
  print "ACross: %0.2f (%d/%d)" % (100.0 * by_and_cross/total, by_and_cross, total)
  print "@Cross: %0.2f (%d/%d)" % (100.0 * by_at_cross/total, by_at_cross, total)
  print "SCross: %0.2f (%d/%d)" % (100.0 * by_street_cross/total, by_street_cross, total)
  for k in sorted(buildings.keys()):
    print "%s: %0.2f (%d/%d)" % (k, 100.0 * buildings[k]/total, buildings[k], total)
  print "From Title: %0.2f (%d/%d)" % (100.0 * from_title/total, from_title, total)
  print "From Location: %0.2f (%d/%d)" % (100.0 * from_location/total, from_location, total)
