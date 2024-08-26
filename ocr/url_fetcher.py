#!/usr/bin/env python
'''Fetch a bunch of URLs and store them permanently on-disk.

Uses requests-cache and a sqlite database.  Does rate-throttling.

Usage:
    ./url_fetcher.py path-to-list-of.urls.txt
'''

import fileinput
import os
import requests
import requests_cache
import time
import sys


class NotInCacheError(Exception):
    pass


class Fetcher(object):
    def __init__(self, throttle_secs=1.0, headers=None):
        self._session = requests_cache.CachedSession('.url_fetcher_cache')
        self._throttle_secs = throttle_secs
        self._last_fetch = 0.0
        self._headers = headers

    def fetch_url(self, url, force_refetch=False):
        if force_refetch:
            self.remove_url_from_cache(url)
        req = self._make_request(url)
        start_t = time.time()
        response = self._session.send(req)
        end_t = time.time()
        response.raise_for_status()  # checks for status == 200 OK

        if not response.from_cache and end_t - self._last_fetch < self._throttle_secs:
            wait_s = end_t - self._last_fetch
            sys.stderr.write('Waiting %s secs...\n' % wait_s)
            time.sleep(wait_s)
        self._last_fetch = end_t

        return response.content

    def is_url_in_cache(self, url):
        return self._cache().has_url(url)

    def fetch_url_from_cache(self, url):
        req = self._make_request(url)
        cache_key = self._cache().create_key(req)
        response = self._cache().get_response(cache_key)
        if not response:
            raise NotInCacheError()
        return response.content

    def remove_url_from_cache(self, url):
        self._cache().delete_url(url)

    def _cache(self):
        return self._session.cache

    def _make_request(self, url):
        # By constructing the request outside the Session, we avoid attaching
        # unwanted cookie headers to subsequent requests, which might break the
        # cache.
        return requests.Request('GET', url, headers=self._headers).prepare()


if __name__ == '__main__':
    f = Fetcher()
    for i, line in enumerate(fileinput.input()):
        line = line.strip()
        if '\t' in line:
            filename, url = line.split('\t')
        else:
            filename = None
            url = line

        print('%5d Fetching %s' % (i + 1, url))
        content = f.fetch_url(url)
        if filename:
            open(filename, 'wb').write(content)
