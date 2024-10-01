#!/usr/bin/env python

import sys
from collections import Counter

from coders import nyc_parks
from data.item import Item, load_items


def print_names(items: list[Item]):
    counts = Counter()
    for item in items:
        for name in item.subject.name:
            counts[name] += 1

    for name, count in counts.most_common():
        print(f"{count}\t{name}")


def print_geographics(items: list[Item]):
    geo_to_loc = {}
    counts = Counter()
    for item in items:
        for raw_g in item.subject.geographic:
            g = raw_g
            counts[g] += 1
            if g.endswith(" (New York, N.Y.)"):
                g = g.replace(" (New York, N.Y.)", "")
            if g in nyc_parks.parks:
                geo_to_loc[raw_g] = nyc_parks.parks[g]

    for name, count in counts.most_common():
        loc = geo_to_loc.get(name) or ""
        print(f"{count}\t{name}\t{loc}")


if __name__ == "__main__":
    kind = sys.argv[1]
    items = load_items("data/images.ndjson")

    if kind == "name":
        print_names(items)
    elif kind == "geographic":
        print_geographics(items)
    else:
        raise ValueError(f"Unknown kind: {kind}")
