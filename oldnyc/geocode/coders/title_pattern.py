"""Geocode by pattern matching against the title.

This matches extremely simple, common patterns that aren't worth a trip to GPT.
"""

import re
import sys

from oldnyc.geocode import grid
from oldnyc.geocode.boroughs import point_to_borough
from oldnyc.geocode.coders.coder_utils import get_lat_lng_from_geocode
from oldnyc.geocode.coders.extended_grid import parse_street_ave
from oldnyc.geocode.geocode_types import Coder, Locatable

boroughs_pat = r"(?:Manhattan|Brooklyn|Queens|Bronx|Staten Island|Richmond)"

# Borough: str1 - str2
# Manhattan: 10th Street (East) - Broadway
# 711023f
boro_int = re.compile(rf"^({boroughs_pat}): ([^-:\[\];]+?) - ([^-:\[\];]+)\.?$")


class TitlePatternCoder(Coder):
    def __init__(self):
        self.n_title = 0
        self.n_alt_title = 0
        self.n_match = 0

        self.n_grid = 0
        self.n_google_location = 0
        self.n_geocode_fail = 0
        self.n_boro_mismatch = 0

    def codeRecord(self, r):
        src = None
        m = boro_int.match(r.title)
        if m:
            src = r.title
            self.n_title += 1
        else:
            for alt_title in r.alt_title:
                m = boro_int.match(alt_title)
                if m:
                    src = alt_title
                    self.n_alt_title += 1
                    break

        if not m:
            return None

        self.n_match += 1

        boro, str1, str2 = m.groups()
        if "and" in str1 or "and" in str2:
            return None
        str1 = str1.rstrip(". ")
        str2 = str2.rstrip(". ")
        (str1, str2) = sorted((str1, str2))  # try to increase cache coherence
        boro = boro.replace("Richmond", "Staten Island")

        assert src
        out: Locatable = {
            "type": "intersection",
            "source": src,
            "address": f"{str1} and {str2}, {boro}, NY",
            "data": (str1, str2, boro),
        }
        return out

    def getLatLonFromGeocode(self, geocode, data, record):
        assert "data" in data
        ssb: tuple[str, str, str] = data["data"]
        (str1, str2, boro) = ssb
        if boro == "Manhattan":
            try:
                avenue, street = parse_street_ave(str1, str2)
                latlon = grid.code(avenue, street)
                if latlon:
                    self.n_grid += 1
                    lat, lng = latlon
                    return round(float(lat), 7), round(float(lng), 7)  # they're numpy floats
            except ValueError:
                pass
        # TODO: use extended-grid coder if possible; would require more street/avenue parsing.

        tlatlng = get_lat_lng_from_geocode(geocode, data)
        if not tlatlng:
            self.n_geocode_fail += 1
            return None
        _, lat, lng = tlatlng
        geocode_boro = point_to_borough(lat, lng)
        if geocode_boro != boro:
            self.n_boro_mismatch += 1
            sys.stderr.write(
                f'Borough mismatch: {record.id}: {data["source"]} geocoded to {geocode_boro} not {boro}\n'
            )
            return None
        self.n_google_location += 1
        return (lat, lng)

    def finalize(self):
        sys.stderr.write(f"    titles matched: {self.n_title}\n")
        sys.stderr.write(f"alt titles matched: {self.n_alt_title}\n")
        sys.stderr.write(f"     total matches: {self.n_match}\n")
        sys.stderr.write("  geocoding results:\n")
        sys.stderr.write(f"            grid: {self.n_grid}\n")
        sys.stderr.write(f"          google: {self.n_google_location}\n")
        sys.stderr.write(f"   boro mismatch: {self.n_boro_mismatch}\n")
        sys.stderr.write(f"        failures: {self.n_geocode_fail}\n")

    def name(self):
        return "title-pattern"
