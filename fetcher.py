import base64
import errno
import hashlib
import os
import sys
import time
import urllib


# From http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
def mkdir_p(path):
  try:
    os.makedirs(path)
  except OSError as exc: # Python >2.5
    if exc.errno == errno.EEXIST:
      pass
    else: raise


class Fetcher:
  """A rate-limited, caching URL fetcher.

  The public API consists of these methods:
  - Fetch(url): fetch from cache or web
  - InCache(url): is the URL stored in the cache?
  - FetchFromCache(url): fetch, but only from cache (returns None otherwise)
  """

  def __init__(self, cache_dir, wait_time_secs):
    self._cache_dir = cache_dir
    self._wait_time = wait_time_secs
    self._last_fetch_time_ = 0


  def Fetch(self, url):
    """Returns data from the URL, possibly from the cache."""
    data = self._check_cache(url)
    from_cache = data != None
    if not data:
      data = self._fetch(url)
    else:
      sys.stderr.write("Cache hit: %s\n" % url)

    if not from_cache and data:
      self._cache_result(url, data)

    return data


  def InCache(self, url):
    """Is the URL in the cache?"""
    data = self._check_cache(url)
    return data == None


  def FetchFromCache(self, url):
    """Like Fetch, but never goes to the network to get a location."""
    return self._check_cache(url)


  def _cache_file(self, url):
    """Returns the path to the cache file for a URL."""
    key = hashlib.md5(url).hexdigest()
    mkdir_p(self._cache_dir)
    return "%s/%s" % (self._cache_dir, key)

  def _check_cache(self, url):
    """Returns cached results for the location or None if not available."""
    cache_file = self._cache_file(url)
    try:
      return file(cache_file).read()
    except:
      return None

  def _cache_result(self, url, result):
    cache_file = self._cache_file(url)
    file(cache_file, "w").write(result)

  def _fetch(self, url):
    """Attempts to fetch the URL. Does rate throttling. Returns content."""
    now = time.time()
    diff = now - self._last_fetch_time_
    if diff < self._wait_time:
      time.sleep(self._wait_time - diff)
    self._last_fetch_time_ = time.time()

    sys.stderr.write("Fetching %s\n" % url)
    f = urllib.URLopener().open(url)
    return f.read()
