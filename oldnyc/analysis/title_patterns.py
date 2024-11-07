#!/usr/bin/env python
"""Get counts for simple patterns in titles."""

import random
import re
from collections import Counter

from oldnyc.item import load_items

boroughs_pat = r"(?:Manhattan|Brooklyn|Queens|Bronx|Staten Island|Richmond)"

# Borough: str1 - str2
# Manhattan: 10th Street (East) - Broadway
# 711023f
boro_int = re.compile(rf"^({boroughs_pat}): ([^-:\[\]]+?) - ([^-:\[\]]+)$")

# Exceptions:
# 711722f, 711033f, 715098f, 715051f, 710728f
# 728266f, 706831f

# Fulton Street at Bond Street, to Northeast, Brooklyn
at_trivia = re.compile(rf"^([^-:\[\]]+?) at ([^-:\[\]]+?)(?: and ?)?, .*, ({boroughs_pat})$")
# Exceptions: 105154

dash = re.compile(r"([^-:\[\]]+?) - ([^-:\[\]]+?)$")

patterns = [("boro_int", boro_int), ("at_trivia", at_trivia), ("dash", dash)]


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

    for item in items:
        is_matched = False
        for pattern_name, pat in patterns:
            m = pat.match(item.title)
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
                    break

        if not is_matched:
            print(f"{item.id} {item.title}")

    print(counts.most_common())


if __name__ == "__main__":
    main()
