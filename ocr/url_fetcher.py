#!/usr/bin/env python
'''Fetch a bunch of URLs and store them permanently on-disk.

Uses requests-cache and a sqlite database.  Does rate-throttling.

Usage:
    ./url_fetcher.py path-to-list-of.urls.txt
'''

import argparse
import os
import requests
import requests_cache
import time
import sys


class NotInCacheError(Exception):
    pass


class Fetcher(object):
    def __init__(self, throttle_secs=1.0, headers=None, ignore_cache=False):
        if not ignore_cache:
            self._session = requests_cache.CachedSession('.url_fetcher_cache')
        else:
            self._session = requests.Session()
        self._ignore_cache = ignore_cache
        self._throttle_secs = throttle_secs
        self._headers = headers

    def fetch_url(self, url, force_refetch=False):
        if force_refetch:
            self.remove_url_from_cache(url)
        req = self._make_request(url)
        start_t = time.time()
        response = self._session.send(req)
        # end_t = time.time()
        response.raise_for_status()  # checks for status == 200 OK

        if (
            self._ignore_cache or not response.from_cache
        ) and time.time() - start_t < self._throttle_secs:
            wait_s = self._throttle_secs - (time.time() - start_t)
            sys.stderr.write('Waiting %s secs...\n' % wait_s)
            time.sleep(wait_s)

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
    parser = argparse.ArgumentParser(
        description="Rate-limited URL fetching with optional caching."
    )
    parser.add_argument(
        "--throttle-secs", default=3.0, type=float, help="Rate limit for HTTP requests."
    )
    parser.add_argument(
        "--overwrite",
        default=False,
        action="store_true",
        help="Re-fetch files that already exist on disk.",
    )
    parser.add_argument(
        "--ignore-cache",
        default=False,
        action="store_true",
        help="Do not check cache, do not cache results",
    )
    parser.add_argument(
        "--header",
        action="append",
        help="Additional headers to set, format is 'key: value'.",
    )
    parser.add_argument(
        "--output-dir", help="Output directory for files (default is CWD)"
    )
    parser.add_argument(
        "urls_file",
        help="Path to file containing URLs, or URL<tab>filename",
    )
    args = parser.parse_args()

    headers = (
        dict(header.split(": ", 1) for header in args.header) if args.header else None
    )

    f = Fetcher(
        ignore_cache=args.ignore_cache,
        throttle_secs=args.throttle_secs,
        headers=headers,
    )
    for i, line in enumerate(open(args.urls_file)):
        line = line.strip()
        if '\t' in line:
            url, filename = line.split("\t")
        else:
            url = line
            filename = url.split("/")[-1]

        if args.output_dir:
            filename = os.path.join(args.output_dir, filename)

        if not args.overwrite and os.path.exists(filename):
            sys.stderr.write(f'{filename} already exists, skipping…\n')
            continue

        print("%5d Fetching %s -> %s" % (i + 1, url, filename))
        content = f.fetch_url(url)
        if filename:
            open(filename, 'wb').write(content)
