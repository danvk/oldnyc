#!/usr/bin/env python
"""Geocode intersections by extending the existing NYC grid.

This lets us cover intersections which no longer exist, but may have in the
past, e.g.

  15th Street and Avenue A
  20th Street and 4th Avenue

This requires grid/intersections.json, which is generated by
grid/extrapolate.py.
"""

import fileinput
import re
import sys

import coders.registration
from data.item import Item, blank_item
from grid import coder

ORDINALS = {
    "First": 1,
    "Second": 2,
    "Third": 3,
    "Fourth": 4,
    "Fifth": 5,
    "Sixth": 6,
    "Seventh": 7,
    "Eighth": 8,
    "Ninth": 9,
    "Tenth": 10,
    "Eleventh": 11,
    "Twelfth": 12,
    # Some NYC-specific stuff
    "Amsterdam": 10,
    r"\bPark\b": 4,  # the \b's prevent this from matching, e.g., 'Parkway'
    "Columbus": 9,
    "West End": 11,
    "Lenox": 6,  # Now Malcolm X
}


def parse_street_ave(street1: str, street2: str) -> tuple[str, str]:
    # try to get the avenue in street1
    if re.search(r"str|st\.", street1, flags=re.I):
        street2, street1 = street1, street2

    if not re.search(r"ave", street1, flags=re.I):
        raise ValueError("%s is not an avenue" % street1)

    if not re.search(r"str|st\.", street2, flags=re.I):
        raise ValueError("%s is not a street" % street2)

    street1 = remove_parens(street1)
    street2 = remove_parens(street2)
    street2 = re.sub(r"West|East", "", street2, flags=re.I)

    # pull the number from the street string
    num = extract_ordinal(street2)
    if num is None:
        raise ValueError("Unable to find a number in %s" % street2)
    street2 = str(num)

    # Try the same for the avenue
    num = extract_ordinal(street1)
    if num is not None:
        street1 = str(num)
    else:
        # Look for something like 'Avenue A'
        m = re.search(r"[aA]venue (A|B|C|D)", street1)
        if m:
            street1 = m.group(1)
        else:
            # How about 'Fourth', 'Fifth'?
            num = multisearch(ORDINALS, street1)
            if num is not None:
                street1 = str(num)
            else:
                raise ValueError("Did not find an avenue in %s" % street1)

    return street1, street2


def remove_parens(txt: str):
    return re.sub(r"\([^)]+\)", "", txt)


def extract_ordinal(txt: str):
    m = re.search(r"(\d+)(?:st|nd|rd|th) ", txt)
    return int(m.group(1)) if m else None


def multisearch(re_dict, txt):
    """Search for any of the keys. Given a match, return the value."""
    for k, v in re_dict.items():
        if re.search(k, txt, flags=re.I):
            return v
    return None


class ExtendedGridCoder:
    def __init__(self):
        # This is done here to avoid the milstein registering itself.
        from coders.milstein import cross_patterns

        self._cross_patterns = cross_patterns

    def _extractLocationStringFromRecord(self, r: Item):
        raw_loc = r.address.strip()
        loc = re.sub(r'^[ ?\t"\[]+|[ ?\t"\]]+$', "", raw_loc)
        return loc

    def codeRecord(self, r: Item):
        loc = self._extractLocationStringFromRecord(r)

        m = None
        for pattern in self._cross_patterns:
            m = re.match(pattern, loc)
            if m:
                break
        if not m:
            return None

        street1, street2, boro = m.groups()
        if not boro.startswith("Manhattan"):
            return None

        try:
            avenue, street = parse_street_ave(street1, street2)
        except ValueError:
            # sys.stderr.write('%s: %s\n' % (loc, str(e)))
            return None

        # Special cases
        photo_id = r.id
        if photo_id.startswith("723557f"):
            # These are mislabeled as 93rd and B.
            avenue, street = "B", "8"
        elif photo_id.startswith("711789") or photo_id.startswith("713187"):
            # Mislabeled as 25th & D. Unclear about the second one.
            avenue, street = "A", "25"
        elif photo_id.startswith("715535f"):
            # Mislabeled as 103rd & 7th instead of 130th & 7th.
            # This incorrectly puts it in the middle of Central Park!
            avenue, street = "7", "130"

        latlon = coder.code(avenue, street)
        if not latlon:
            return None

        # sys.stderr.write('coded (%s, %s) --> (%s, %s)\n' % (street1, street2, avenue, street))

        return {
            "address": "@%.6f,%.6f" % latlon,
            "source": loc,
            "grid": "(%s, %s)" % (avenue, street),
            "type": "intersection",
        }

    def getLatLonFromGeocode(self, geocode, data, r):
        for result in geocode["results"]:
            # data['type'] is something like 'address' or 'intersection'.
            if "point_of_interest" in result["types"]:
                loc = result["geometry"]["location"]
                return (loc["lat"], loc["lng"])

    def finalize(self):
        sys.stderr.write("       num_exact: %d\n" % coder.num_exact)
        sys.stderr.write("num_extrapolated: %d\n" % coder.num_extrapolated)
        sys.stderr.write("   num_unclaimed: %d\n" % coder.num_unclaimed)

    def name(self):
        return "extended-grid"


coders.registration.registerCoderClass(ExtendedGridCoder)


# For fast iteration
if __name__ == "__main__":
    grid_coder = ExtendedGridCoder()
    num_ok, num_bad = 0, 0
    for line in fileinput.input():
        addr = line.strip()
        if not addr:
            continue
        r = blank_item()
        r.address = addr
        result = grid_coder.codeRecord(r)

        print('"%s" -> %s' % (addr, result))
        if result:
            num_ok += 1
        else:
            num_bad += 1

    sys.stderr.write(
        "Parsed %d / %d = %.4f records\n"
        % (num_ok, num_ok + num_bad, 1.0 * num_ok / (num_ok + num_bad))
    )
