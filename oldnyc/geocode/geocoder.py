#!/usr/bin/python
#
# Run addresses or cross-streets through the Google Maps geocoder.
#
# Maintains a cache of previously-geocoded locations and throttles traffic to the Geocoder.

import base64
import json
import re
import sys
import time
import urllib
import urllib.parse
import urllib.request
from typing import Any, Optional

GeocodeUrlTemplate = "https://maps.googleapis.com/maps/api/geocode/json?sensor=false&address=%s"
CacheDir = "geocache"

CacheDebug = False
# CacheDebug = True

# For lat/lon requests, where we can skip the geocoder.
FakeResponse = """
{ "results" : [ {
   "geometry" : { "location" : { "lat" : %s, "lng" : %s } },
   "types" : [ "point_of_interest" ]
  } ], "status" : "OK" }
"""


def cache_file_name(loc: str):
    key = base64.b64encode(loc.encode("utf8"))[:-2].decode("ascii")  # minus the trailing '=='
    key = key.replace("/", "-")  # '/' is bad in a file name.
    key = key[:255]  # longest possible filename
    return "%s/%s" % (CacheDir, key)


class Geocoder:
    def __init__(self, network_allowed: bool, wait_time: int, api_key: Optional[str] = None):
        self._network_allowed = network_allowed
        self._wait_time = wait_time
        self._last_fetch = 0
        self._api_key = api_key
        self._touched_cache_files = set()
        self.n_cache_misses = 0

    def _check_cache(self, loc: str):
        """Returns cached results for the location or None if not available."""
        cache_file = cache_file_name(loc)
        self._touched_cache_files.add(cache_file)
        if CacheDebug:
            sys.stderr.write("Checking %s\n" % cache_file)
        try:
            return open(cache_file).read()
        except Exception:
            return None

    def _cache_result(self, loc: str, result: bytes):
        cache_file = cache_file_name(loc)
        open(cache_file, "wb").write(result)

    def _fetch(self, url: str, debug_txt: Optional[str]):
        """Attempts to fetch the URL. Does rate throttling. Returns XML."""
        now = time.time()
        diff = now - self._last_fetch
        sys.stderr.write(
            "now=%f, then=%f, diff=%f vs. %f\n" % (now, self._last_fetch, diff, self._wait_time)
        )
        if diff < self._wait_time:
            time.sleep(self._wait_time - diff)
        self._last_fetch = time.time()

        sys.stderr.write(f"Fetching {url} ({debug_txt})\n")
        assert self._api_key
        # Note: API key is _not_ part of the cache key
        f = urllib.request.urlopen(url + "&key=" + self._api_key)
        return f.read()

    def _check_for_lat_lon(self, address: str):
        """For addresses of the form "@(lat),(lon)", skip the geocoder."""
        m = re.match(r"@([-0-9.]+),([-0-9.]+)$", address)
        if m:
            return FakeResponse % (m.group(1), m.group(2))

    # TODO: get a more precise return type from the GMaps API
    def Locate(
        self, address: str, check_cache=True, debug_txt: Optional[str] = None
    ) -> dict[str, Any] | None:
        """Returns a maps API JSON response for the address or None.

        Address should be a fully-qualified address, e.g.
        '111 8th Avenue, New York, NY'.
        """
        url = GeocodeUrlTemplate % urllib.parse.quote(address)

        data = None
        from_cache = False
        is_lat_lng = False
        if check_cache:
            data = self._check_cache(address)
            from_cache = data is not None
        if not data:
            data = self._check_for_lat_lon(address)
            is_lat_lng = data is not None  # no point in caching these
        if not data:
            if not self._network_allowed:
                self.n_cache_misses += 1
                sys.stderr.write(f"Would have geocoded with network: {address}\n")
                # XXX this should probably raise instead
                return None
            data = self._fetch(url, f"{debug_txt}: {address}")

        if not data:
            return None

        response = json.loads(data)
        status = response["status"]
        if status not in ["OK", "ZERO_RESULTS"]:
            sys.stderr.write("Error status %s %s\n" % (status, json.dumps(response)))
            if status == "OVER_QUERY_LIMIT":
                raise Exception("Over your quota for the day!")

            return None
        if not (from_cache or is_lat_lng) and response:
            self._cache_result(address, data)  # type: ignore

        return response

    def log_stats(self):
        sys.stderr.write("Google geocoder stats:\n")
        sys.stderr.write(f"     Cache misses: {self.n_cache_misses}\n")
        sys.stderr.write(f"  Cache files hit: {self._touched_cache_files}\n")


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        print("%s --> %s" % (arg, cache_file_name(arg)))
