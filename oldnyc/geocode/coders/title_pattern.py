"""Geocode by pattern matching against the title.

This matches extremely simple, common patterns that aren't worth a trip to GPT.
"""

import re
import sys
from collections import Counter

from natsort import natsorted

from oldnyc.geocode import grid
from oldnyc.geocode.boroughs import point_to_borough
from oldnyc.geocode.coders.coder_utils import get_lat_lng_from_geocode
from oldnyc.geocode.coders.extended_grid import parse_street_ave
from oldnyc.geocode.geocode_types import Coder, Locatable
from oldnyc.geocode.record import clean_title
from oldnyc.item import Item

boroughs_pat = r"(?:Manhattan|Brooklyn|Queens|Bronx|Staten Island|Richmond)"

# Borough: str1 - str2
# Manhattan: 10th Street (East) - Broadway
# 711023f
boro_int = re.compile(rf"^({boroughs_pat})(?::| -) ([^-:\[\];]+?) - ([^-:\[\];]+)\.?$")

at_int = re.compile(rf"^([^-:\[\];]+?) at ([^-:\[\];]+), ({boroughs_pat})\.?$")

between = re.compile(
    rf"^({boroughs_pat}): ([^-:\[\];]+?) - [bB]etween ([^-:\[\];]+?) and ([^-:\[\];]+)\.?$"
)

num_prefix = re.compile(rf"^({boroughs_pat})(?::| -) \d+ ([^-:\[\];]+?) - ([^-:\[\];]+)\.?$")

PATTERNS = [
    ("between", between),
    ("num-prefix", num_prefix),
    ("boro-int", boro_int),
    ("at-int", at_int),
]


def is_in_manhattan(r: Item):
    return "Manhattan (New York, N.Y.)" in r.subject.geographic or r.source.endswith("Manhattan")


def strip_trivia(txt: str) -> str:
    return re.sub(
        r"to|Northeast|Northwest|Southeast|Southwest|north|east|west|south|side|corner",
        "",
        txt,
        flags=re.I,
    )


def clean_and_strip_title(title: str) -> str:
    title = clean_title(title)
    title = re.sub(r" +:", ":", title)
    # east side
    # west corner
    # north from
    # West side to
    # to Northeast
    parts = re.split(r"( - |, )", title)
    out = []
    for part in parts:
        stripped = strip_trivia(part)
        if not stripped.strip():
            continue
        if part.endswith(" and "):
            part = part[:-5]
        if not out or out[-1] != stripped:
            out.append(part)

    return "".join(out)


def extract_braced_clauses(txt: str) -> list[str]:
    return re.findall(r"\[([^\[\]]+)\]", txt)


class TitlePatternCoder(Coder):
    def __init__(self):
        self.n_title = 0
        self.n_alt_title = 0
        self.n_match = 0
        self.counts = Counter[str]()

        self.n_grid = 0
        self.n_google_location = 0
        self.n_geocode_fail = 0
        self.n_boro_mismatch = 0

    def findMatch(self, r):
        titles = [r.title] + r.alt_title
        titles += [clause for t in titles for clause in extract_braced_clauses(t)]
        splits = []
        for title in titles:
            if ";" in title:
                splits.extend(t.strip() for t in title.split(";"))
        titles += splits

        adds = [False, True] if is_in_manhattan(r) else [False]

        for add in adds:
            for pat_name, pat in PATTERNS:
                for i, title in enumerate(titles):
                    title = clean_and_strip_title(title)
                    if add and not title.startswith("Manhattan"):
                        title = f"Manhattan: {title}"
                    m = pat.match(title)
                    if m:
                        self.counts["title" if i == 0 else "alt_title"] += 1
                        self.counts[pat_name] += 1
                        if pat_name == "at-int":
                            str1, str2, boro = m.groups()
                            return (boro, str1, str2), title
                        return m.groups(), title

    def codeRecord(self, r):
        match = self.findMatch(r)
        if not match:
            return None

        m, src = match
        self.n_match += 1

        boro, str1, str2 = m[:3]
        if re.search(r"\band\b", str1) or re.search(r"\band\b", str2):
            return None

        if len(m) > 3:
            # Normalize "Between 23rd and 24th Streets" -> "23rd Street", "24th Street"
            str3 = m[3]
            if ("Streets" in str3 or "Street" in str3) and "Street" not in str2:
                str2 = str2 + " Street"
                str3 = str3.replace("Streets", "Street")
                str2, str3 = natsorted((str2, str3))
            if ("Avenues" in str3 or "Avenue" in str3) and "Avenue" not in str2:
                str2 = str2 + " Avenue"
                str3 = str3.replace("Avenues", "Avenue")
                str2, str3 = natsorted((str2, str3))

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

    def getLatLonFromLocatable(self, r, data):
        assert "data" in data
        ssb: tuple[str, str, str] = data["data"]
        (str1, str2, boro) = ssb
        if boro != "Manhattan":
            return None
        try:
            avenue, street = parse_street_ave(str1, str2)
            latlon = grid.code(avenue, street)
            if latlon:
                self.n_grid += 1
                lat, lng = latlon
                return round(float(lat), 7), round(float(lng), 7)  # they're numpy floats
        except ValueError:
            pass

    def getLatLonFromGeocode(self, geocode, data, record):
        assert "data" in data
        ssb: tuple[str, str, str] = data["data"]
        (str1, str2, boro) = ssb
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
        sys.stderr.write(f"          counters: {self.counts.most_common()}\n")
        sys.stderr.write("  geocoding results:\n")
        sys.stderr.write(f"            grid: {self.n_grid}\n")
        sys.stderr.write(f"          google: {self.n_google_location}\n")
        sys.stderr.write(f"   boro mismatch: {self.n_boro_mismatch}\n")
        sys.stderr.write(f"        failures: {self.n_geocode_fail}\n")

    def name(self):
        return "title-pattern"
