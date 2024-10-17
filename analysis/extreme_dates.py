#!/usr/bin/env python
"""Print out photo URLs with very early or very late dates.

Very early is pre-1860.
Very late is post-1945.

See https://github.com/danvk/oldnyc/issues/3
"""

import re

from oldnyc.item import load_items


def extract_dates(date_str):
    return re.findall(r"\b(1[6789]\d\d)\b", date_str)


if __name__ == "__main__":
    rs = load_items("data/images.ndjson")
    for r in rs:
        for d in extract_dates(r.date or ""):
            if d < "1860" or d > "1945":
                print("%4s\t%s\t%s" % (d, r.id, r.url))
