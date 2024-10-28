#!/usr/bin/env python
"""Fetch a bunch of URLs with a rate limit.

Usage:
    ./url_fetcher.py path-to-list-of.urls.txt
"""

import argparse
import os
import sys
import time

import requests
from tqdm import tqdm

last_fetch_secs = None


def fetch_url(url: str, headers: dict | None = None, throttle_secs: float = 0) -> bytes:
    global last_fetch_secs
    if last_fetch_secs:
        elapsed = time.time() - last_fetch_secs
        if elapsed < throttle_secs:
            time.sleep(throttle_secs - elapsed)

    last_fetch_secs = time.time()
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # checks for status == 200 OK

    return response.content


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rate-limited URL fetching with optional caching.")
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
        "--header",
        action="append",
        help="Additional headers to set, format is 'key: value'.",
    )
    parser.add_argument("--output-dir", help="Output directory for files (default is CWD)")
    parser.add_argument(
        "urls_file",
        help="Path to file containing URLs, or URL<tab>filename",
    )
    args = parser.parse_args()

    headers = dict(header.split(": ", 1) for header in args.header) if args.header else None

    num_skipped = 0
    pairs = []
    for i, line in enumerate(open(args.urls_file)):
        line = line.strip()
        if "\t" in line:
            url, filename = line.split("\t")
        else:
            url = line
            filename = url.split("/")[-1]

        if args.output_dir:
            filename = os.path.join(args.output_dir, filename)

        if not args.overwrite and os.path.exists(filename):
            num_skipped += 1
            continue
        pairs.append((url, filename))

    if num_skipped:
        sys.stderr.write(f"Skipped {num_skipped} already-fetched files\n")

    for i, (url, filename) in enumerate(tqdm(pairs)):
        # print(i, url, filename)
        if i % 100 == 0:
            print("%5d Fetching %s -> %s" % (i + 1, url, filename))
        content = fetch_url(url, headers, args.throttle_secs)
        if filename:
            open(filename, "wb").write(content)
