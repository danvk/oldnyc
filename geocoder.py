#!/usr/bin/python
#
# Run addresses or cross-streets through the Google Maps geocoder.
#
# Maintains a cache of previously-geocoded locations and throttles traffic to the Geocoder.

import base64
import xml.dom.minidom
import os
import time
import urllib

# MapsKey = "ABQIAAAAafDALeUVyxhUndZQcT0BRRQjgiEk1Ut90lZbiCSD8tXKcVgrkBQLYOFQ3xwutc5R9SNzfGaKxMnf7g"
BaseURL = "http://maps.google.com/maps/geo?output=xml&key=%s"
CacheDir = "geocache"

class Location:
  """Provides status, lat, lon, city, zip, accuracy fields"""
  def __init__(self, dom):
    els = dom.getElementsByTagName("code")
    assert els.length == 1
    self.status = int(els.item(0).firstChild.nodeValue)
    self.lat, self.lon = None, None

    # keep it around just in case
    # self._dom = dom

    # Just take the first place for now
    places = dom.getElementsByTagName("Placemark")
    if len(places) == 0: return
    place = places[0]

    # Geocoding accuracy
    details = place.getElementsByTagName("AddressDetails")
    if len(details) > 0:
      self.accuracy = int(details[0].getAttribute("Accuracy"))

    # Lat/Lon
    coord = place.getElementsByTagName("coordinates")
    if len(coord) >= 1:
      lon, lat, z = coord[0].firstChild.nodeValue.split(",")
      self.lat, self.lon = float(lat), float(lon)

    # City
    cities = place.getElementsByTagName("LocalityName")
    if len(cities) >= 1:
      self.city = cities[0].firstChild.nodeValue

    # Zip Code
    zips = place.getElementsByTagName("PostalCodeNumber")
    if len(zips) >= 1:
      self.zipcode = int(zips[0].firstChild.nodeValue)

  def __str__(self):
    if self.lat and self.lon:
      return "(%f, %f)" % (self.lat, self.lon)
    else:
      return "(???)"


def _cache_file(loc):
  key = base64.b64encode(loc)[:-2]  # minus the trailing '=='
  return "%s/%s" % (CacheDir, key)

class Geocoder:
  def __init__(self, maps_key, wait_time):
    self._api_key = maps_key
    self._base_url = BaseURL % self._api_key
    self._wait_time = wait_time
    self._last_fetch = 0

  def _check_cache(self, loc):
    """Returns cached results for the location or None if not available."""
    cache_file = _cache_file(loc)
    try:
      return file(cache_file).read()
    except:
      return None

  def _cache_result(self, loc, result):
    cache_file = _cache_file(loc)
    file(cache_file, "w").write(result)

  def _parse_xml(self, xml_str):
    """Returns a (lat, lon) pair based on XML"""
    dom = xml.dom.minidom.parseString(xml_str)
    loc = Location(dom)
    return loc

  def _fetch(self, url):
    """Attempts to fetch the URL. Does rate throttling. Returns XML."""
    now = time.time()
    diff = now - self._last_fetch
    print "now=%f, then=%f, diff=%f vs. %f" % (now, self._last_fetch, diff, self._wait_time)
    if diff < self._wait_time:
      time.sleep(self._wait_time - diff)
    self._last_fetch = time.time()

    print "Fetching %s" % url
    f = urllib.URLopener().open(url)
    return f.read()

  def Locate(self, loc):
    """Returns a Location object based on the loc string or None."""
    sf_loc = loc + " San Francisco, CA"
    url = "%s&q=%s" % (self._base_url, urllib.quote(sf_loc))

    data = self._check_cache(loc)
    from_cache = data != None
    if not data:
      data = self._fetch(url)

    location = self._parse_xml(data)
    if not from_cache and location:
      self._cache_result(loc, data)

    return location

  def LocateFromCache(self, loc):
    """Like Locate, but never goes to the network to get a location."""
    data = self._check_cache(loc)
    if not data: return None
    return self._parse_xml(data)
