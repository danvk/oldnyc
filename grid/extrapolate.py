#!/usr/bin/env python
"""Extrapolate the Manhattan grid to non-existent intersections.

This extends the contemporary (2014) grid to cover intersections which no
longer exist, but may have in the past, e.g.

  15th Street and Avenue A
  20th Street and 4th Avenue
"""

import json
import re
from collections import defaultdict

data = json.load(open("nyc-records.json"))

cross_pat = re.compile(r"^(.*) and (.*), Manhattan")
ordinal_street = re.compile(r"(\d+)(?:st|nd|rd|th) (?:Street|Avenue)")
ew_pat = re.compile(r" \((East|West)\)")

by_street = defaultdict(lambda: {})

for row in data:
    if "extracted" not in row:
        continue
    loc_str = row["extracted"].get("located_str")
    if not loc_str:
        continue
    loc_str = re.sub(ew_pat, "", loc_str)
    m = cross_pat.match(loc_str)
    if not m:
        continue
    lat, lon = row["extracted"]["latlon"]

    street1, street2 = m.group(1), m.group(2)

    m1 = ordinal_street.search(street1)
    m2 = ordinal_street.search(street2)

    if m1 and street2 == "Avenue A" and int(m1.group(1)) == 15:
        print(row)
        print(loc_str)

    if m2:
        by_street[street1][int(m2.group(1))] = (lat, lon)
    if m1:
        by_street[street2][int(m1.group(1))] = (lat, lon)

# TODO:
# - normalize streets (e.g. "6th Avenue", "6th Avenue (Southeast)." "[6th Avenue.]"
# - filter addresses, e.g. "300 Park Avenue", "655 Park Avenue"
# - interpolate streets
# - many bad values, e.g. "Avenue A" / "91"

# bad values...
# '15th Street (East) and Avenue A, Manhattan, NY' -->
# geocache/MTV0aCBTdHJlZXQgKEVhc3QpIGFuZCBBdmVudWUgQSwgTWFuaGF0dGFuLCBOWQ
# --> has results for 15th Street & 5th Avenue

json.dump(by_street, open("grid/intersections.json", "w"), indent=2)
