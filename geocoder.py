#!/usr/bin/python
#
# Run addresses or cross-streets through the Google Maps geocoder.
#
# Maintains a cache of previously-geocoded locations and throttles traffic to the Geocoder.

import base64
import os
import sys
import time
import json
import urllib

GeocodeUrlTemplate = 'https://maps.googleapis.com/maps/api/geocode/json?sensor=false&address=%s'
CacheDir = "geocache"

CacheDebug = False
# CacheDebug = True


def _cache_file(loc):
  key = base64.b64encode(loc)[:-2]  # minus the trailing '=='
  key = key.replace('/', '-')  # '/' is bad in a file name.
  key = key[:255]  # longest possible filename
  return "%s/%s" % (CacheDir, key)


class Geocoder:
  def __init__(self, network_allowed, wait_time):
    self._network_allowed = network_allowed
    self._wait_time = wait_time
    self._last_fetch = 0

  def _check_cache(self, loc):
    """Returns cached results for the location or None if not available."""
    cache_file = _cache_file(loc)
    if CacheDebug:
      sys.stderr.write('Checking %s\n' % cache_file);
    try:
      return file(cache_file).read()
    except:
      return None

  def _cache_result(self, loc, result):
    cache_file = _cache_file(loc)
    file(cache_file, "w").write(result)

  def _fetch(self, url):
    """Attempts to fetch the URL. Does rate throttling. Returns XML."""
    now = time.time()
    diff = now - self._last_fetch
    sys.stderr.write("now=%f, then=%f, diff=%f vs. %f\n" % (
        now, self._last_fetch, diff, self._wait_time))
    if diff < self._wait_time:
      time.sleep(self._wait_time - diff)
    self._last_fetch = time.time()

    sys.stderr.write("Fetching %s\n" % url)
    f = urllib.URLopener().open(url)
    return f.read()

  def Locate(self, address, check_cache=True):
    """Returns a maps API JSON response for the address or None.
    
    Address should be a fully-qualified address, e.g.
    '111 8th Avenue, New York, NY'.
    """
    url = GeocodeUrlTemplate % urllib.quote(address)

    data = None
    from_cache = False
    if check_cache:
      data = self._check_cache(address)
      from_cache = data != None
    if not data:
      if not self._network_allowed:
        return None
      data = self._fetch(url)

    if not data:
      return None

    response = json.loads(data)
    if response['status'] not in ['OK', 'ZERO_RESULTS']:
      sys.stderr.write('Error status %s %s\n' % (
          response['status'], json.dumps(response)))
      return None
    if not from_cache and response:
      self._cache_result(address, data)

    return response

  def InCache(self, loc):
    data = self._check_cache(loc)
    return data == None

  def LocateFromCache(self, loc):
    """Like Locate, but never goes to the network to get a location."""
    data = self._check_cache(loc)
    if not data: return None
    return json.loads(data)


if __name__ == '__main__':
  for arg in sys.argv[1:]:
    print '%s --> %s' % (arg, _cache_file(arg))
