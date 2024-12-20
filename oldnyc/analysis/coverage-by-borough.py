#!/usr/bin/env python
"""Reports the fraction of successful geocodes by borough."""

import json
import re
import sys
from collections import defaultdict

from oldnyc.geocode.boroughs import point_to_borough

# This expects input in records.json format, which I've deleted from geocode.py.
# TODO: if I want to run this script again, use one of the other formats.
records = json.load(open(sys.argv[1]))

boros_re = r"(New York|Manhattan|Brooklyn|Bronx|Queens|Staten Island), (?:NY|N\.Y\.)$"

total_by_borough = defaultdict(int)
wrong_by_borough = defaultdict(int)
correct_by_borough = defaultdict(int)

bk_fail = open("/tmp/bkwrong.txt", "w")

for rec in records:
    m = re.search(boros_re, rec["folder"])
    if not m:
        total_by_borough["Unknown"] += 1
        continue
    boro = m.group(1)

    if boro == "New York":
        boro = "Manhattan"
    total_by_borough[boro] += 1

    if "extracted" not in rec:
        continue
    e = rec["extracted"]
    if "latlon" not in e:
        if boro == "Brooklyn":
            bk_fail.write("%s\t%s\n" % (rec["id"], rec["folder"]))
        continue
    if "located_str" not in e:
        continue
    lat, lon = e["latlon"]
    geocode_boro = point_to_borough(lat, lon)

    if boro == geocode_boro:
        correct_by_borough[boro] += 1
    else:
        wrong_by_borough[boro] += 1

for b in sorted(total_by_borough.keys()):
    total = total_by_borough[b]
    correct = correct_by_borough[b]
    print(
        "%.4f (%5d / %5d) %s (%d to wrong borough)"
        % (1.0 * correct / total, correct, total, b, wrong_by_borough[b])
    )
