"""Geocode by pattern matching against the title.

This matches extremely simple, common patterns that aren't worth a trip to GPT.
"""

import re
import sys
from collections import Counter

from natsort import natsorted

from oldnyc.geocode.boroughs import boroughs_pat, guess_borough
from oldnyc.geocode.geocode_types import AddressLocation, Coder, IntersectionLocation
from oldnyc.item import Item

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

num_pattern = re.compile(r"#\d+")  # these are addresses that can throw off geocoding


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
    title = title.replace("[", "").replace("]", "")
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


def extract_titles(r: Item) -> list[str]:
    titles = [r.title] + r.alt_title
    titles += [clause for t in titles for clause in extract_braced_clauses(t)]
    splits = []
    for title in titles:
        if ";" in title:
            splits.extend(t.strip() for t in title.split(";"))
    titles += splits
    return titles


def punctuate(street: str) -> str:
    """Add a trailing dot to a street if it might make sense"""
    # Blvd intentionally omitted
    if street.endswith(
        ("St", "Ave", "Rd", "Hwy", "Pl", "S", "N", "E", "W")
    ) and not street.endswith(("Avenue S", "Avenue N", "Avenue W", "Avenue E", "Ave. W")):
        return street + "."
    return street


class TitleCrossCoder(Coder):
    def __init__(self):
        self.n_title = 0
        self.n_alt_title = 0
        self.n_match = 0
        self.counts = Counter[str]()

        self.n_grid = 0
        self.n_grid_attempt = 0
        self.n_grid_parse = 0
        self.n_google_location = 0
        self.n_geocode_fail = 0
        self.n_boro_mismatch = 0

    def findMatch(self, r):
        titles = extract_titles(r)
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

    def code_record(self, r: Item):
        loc = self.code_one_record(r)
        if loc:
            return [loc]

    def code_one_record(self, r: Item):
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

        str1 = re.sub(num_pattern, "", str1).rstrip(". ,")
        str2 = re.sub(num_pattern, "", str2).rstrip(". ,")
        (str1, str2) = sorted((str1, str2))  # try to increase cache coherence
        boro = boro.replace("Richmond", "Staten Island")

        # This makes the streets look more like the milstein coder, which
        # improves cache coherence and consistency.
        # TODO: is this still relevant with the OSM grid coder?
        str1 = punctuate(str1)
        str2 = punctuate(str2)
        assert src
        return IntersectionLocation(source=src, str1=str1, str2=str2, boro=boro)

    def finalize(self):
        sys.stderr.write(f"    titles matched: {self.n_title}\n")
        sys.stderr.write(f"alt titles matched: {self.n_alt_title}\n")
        sys.stderr.write(f"     total matches: {self.n_match}\n")
        sys.stderr.write(f"          counters: {self.counts.most_common()}\n")

    def name(self):
        return "title-cross"


# Cribbed from milstein.py, which I hope to delete.
# (?P<street1>[^#]+)
streets_pat = r"(?:St\.|Street|Place|Pl\.|Road|Rd\.|Avenue|Ave\.|Av\.|Boulevard|Blvd\.|Broadway|Parkway|Pkwy\.|Pky\.|Street \(West\)|Street \(East\))"

address1_re = re.compile(rf"^([^-:;]+ {streets_pat}) #(\d+)")
address2_re = re.compile(rf"^(\d+) ([^-:;]+ {streets_pat})")

ADDR_PATTERNS = [
    ("street_pound", address1_re),
    ("num_street", address2_re),
]


def rewrite_directional_street(street: str) -> str:
    """Rewrite "34th Street (West)" -> "W 34th Street"."""
    m = re.match(r"(\d+(?:th|st|nd|rd)) Street \((North|South|East|West)\)", street)
    if m:
        num, dir = m.groups()
        return f"{dir[0]} {num} Street"
    return street


class TitleAddressCoder(Coder):
    def __init__(self):
        self.n_matches = 0
        self.n_success = 0
        self.n_geocode_fail = 0
        self.n_boro_mismatch = 0
        self.patterns = Counter[str]()

    def code_record(self, r: Item):
        loc = self.code_one_record(r)
        if loc:
            return [loc]

    def code_one_record(self, r: Item):
        titles = extract_titles(r)
        for t in titles:
            for name, pat in ADDR_PATTERNS:
                m = re.search(pat, t)
                if m:
                    # TODO: use named capture groups
                    if name == "num_street":
                        num, street = m.groups()
                    else:
                        street, num = m.groups()
                    boro = guess_borough(r) or "Manhattan"
                    self.n_matches += 1
                    street = rewrite_directional_street(street)
                    self.patterns[name] += 1
                    return AddressLocation(
                        source=m.group(0),
                        num=int(num),
                        street=street,
                        boro=boro,
                    )

    def finalize(self):
        sys.stderr.write(f" address matches: {self.n_matches}\n")
        sys.stderr.write(f"        patterns: {self.patterns.most_common()}\n")

    def name(self):
        return "title-address"
