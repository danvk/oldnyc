#!/usr/bin/env python

import sys

from crawl.roots import get_nypl_fetcher

if __name__ == "__main__":
    f = get_nypl_fetcher()
    url = sys.argv[1]
    outfile = sys.argv[2] if len(sys.argv) > 2 else None
    r = f.fetch_url_from_cache(url)
    if outfile:
        with open(outfile, "wb") as out:
            out.write(r)
    else:
        sys.stdout.write(r.decode("utf-8"))
