#!/usr/bin/env python
"""Get counts for simple patterns in titles."""

import random
import re
from collections import Counter

import pygeojson

from oldnyc.item import load_items

boroughs_pat = r"(?:Manhattan|Brooklyn|Queens|Bronx|Staten Island|Richmond)"

# Borough: str1 - str2
# Manhattan: 10th Street (East) - Broadway
# 711023f
boro_int = re.compile(rf"^({boroughs_pat}): ([^-:\[\]]+?) - ([^-:\[\]]+)\.?$")

# Exceptions:
# 711722f, 711033f, 715098f, 715051f, 710728f
# 728266f, 706831f

# Fulton Street at Bond Street, to Northeast, Brooklyn
at_trivia = re.compile(rf"^([^-:\[\]]+?) at ([^-:\[\]]+?)(?: and ?)?, .*, ({boroughs_pat})$")
# Exceptions: 105154

dash = re.compile(r"([^-:\[\]]+?) - ([^-:\[\]]+?)$")

patterns = [("boro_int", boro_int)]  # , ("at_trivia", at_trivia), ("dash", dash)]


def is_balanced(s: str):
    n = 0
    for c in s:
        if c == ")":
            if n == 0:
                return False
            n -= 1
        elif c == "(":
            n += 1
    return n == 0


def main():
    items = load_items("data/images.ndjson")
    counts = Counter[str]()
    random.shuffle(items)
    n_alt = 0
    techs = Counter[str | None]()

    features = pygeojson.load_feature_collection(open("/tmp/images.geojson")).features
    id_to_tech = {f.id: f.properties["geocode"]["technique"] for f in features if f.geometry}

    for item in items:
        is_matched = False
        for i, t in enumerate([item.title] + item.alt_title):
            if is_matched:
                break
            is_alt = i > 0
            for pattern_name, pat in patterns:
                m = pat.match(t)
                if m:
                    if pattern_name == "dash":
                        a, b = m.groups()
                        if is_balanced(a) and is_balanced(b):
                            counts[pattern_name] += 1
                            # print(f"{pattern_name}: {item.id} {m.groups()}")
                            is_matched = True
                            break
                    else:
                        counts[pattern_name] += 1
                        # print(f"{pattern_name}: {item.id} {m.groups()}")
                        is_matched = True
                        if is_alt:
                            n_alt += 1
                        else:
                            tech = id_to_tech.get(item.id)
                            techs[tech] += 1
                        break

        # if not is_matched:
        #     print(f"{item.id} {item.title}")

    print(counts.most_common())
    print(f"{n_alt=}")
    print(techs.most_common())


if __name__ == "__main__":
    main()
