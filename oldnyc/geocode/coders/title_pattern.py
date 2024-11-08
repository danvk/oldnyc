"""Geocode by pattern matching against the title.

This matches extremely simple, common patterns that aren't worth a trip to GPT.
"""

import re
import sys

from oldnyc.geocode.coders.coder_utils import get_lat_lng_from_geocode
from oldnyc.geocode.geocode_types import Coder, Locatable

boroughs_pat = r"(?:Manhattan|Brooklyn|Queens|Bronx|Staten Island|Richmond)"

# Borough: str1 - str2
# Manhattan: 10th Street (East) - Broadway
# 711023f
boro_int = re.compile(rf"^({boroughs_pat}): ([^-:\[\]]+?) - ([^-:\[\]]+)\.?$")


class TitlePatternCoder(Coder):
    def __init__(self):
        self.n_title = 0
        self.n_alt_title = 0
        self.n_match = 0

    def codeRecord(self, r):
        m = boro_int.match(r.title)
        if m:
            self.n_title += 1
        else:
            for alt_title in r.alt_title:
                m = boro_int.match(alt_title)
                if m:
                    self.n_alt_title += 1
                    break

        if not m:
            return None

        self.n_match += 1

        boro, str1, str2 = m.groups()
        if "and" in str1 or "and" in str2:
            return None
        (str1, str2) = sorted((str1, str2))  # try to increase cache coherence
        boro = boro.replace("Richmond", "Staten Island")

        # TODO: try out "str1 & str2" instead of "str1 and str2".
        #       I'm using the latter for cache coherence, but the former might work better.
        out: Locatable = {
            "type": "intersection",
            "source": r.title,
            "address": f"{str1} and {str2}, {boro}, NY",
        }
        return out

    def getLatLonFromGeocode(self, geocode, data, record):
        tlatlng = get_lat_lng_from_geocode(geocode, data)
        if not tlatlng:
            return None
        _, lat, lng = tlatlng
        return (lat, lng)

    def finalize(self):
        sys.stderr.write(f"    titles matched: {self.n_title}\n")
        sys.stderr.write(f"alt titles matched: {self.n_alt_title}\n")
        sys.stderr.write(f"     total matches: {self.n_match}\n")

    def name(self):
        return "title-pattern"
