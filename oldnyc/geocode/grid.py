#!/usr/bin/env python

import csv
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Sequence

import numpy as np
from pygeojson import Optional
from word2number import w2n

Point = tuple[float, float]


@dataclass(frozen=True, init=False)
class Intersection:
    def __init__(self, str1: str, str2: str, boro: str):
        str1, str2 = (str1, str2) if str1 < str2 else (str2, str1)
        # See https://stackoverflow.com/a/58336722/388951
        object.__setattr__(self, "str1", str1)
        object.__setattr__(self, "str2", str2)
        object.__setattr__(self, "boro", boro)

    str1: str
    str2: str
    boro: str


def load_mini_grid():
    by_avenue = defaultdict[str, dict[int, Point]](dict)
    by_street = defaultdict[int, dict[str, Point]](dict)
    for row in csv.DictReader(open("data/grid.csv")):
        if not row["Lat"]:
            continue  # not all intersections exist.
        avenue = int(row["Avenue"])
        street = int(row["Street"])
        lat = float(row["Lat"])
        lon = float(row["Lon"])
        if avenue <= 0:
            avenue = ["A", "B", "C", "D"][-avenue]
        else:
            avenue = str(avenue)
        pt = (lat, lon)
        by_avenue[avenue][street] = pt
        by_street[street][avenue] = pt

    return by_avenue, by_street


def load_manhattan_intersections():
    all_ints = defaultdict[int, dict[str, Point]](dict)
    all_ints_by_ave = defaultdict[str, dict[int, Point]](dict)

    # TODO: maybe this is a subset of nyc-intersections.csv?
    for row in csv.DictReader(open("data/intersections.csv")):
        street = int(row["Street"])
        raw_avenue = row["Avenue"]
        lat = float(row["Lat"])
        lon = float(row["Lon"])
        avenue = parse_ave(raw_avenue)
        if avenue is not None:
            all_ints[street][avenue] = (lat, lon)
        all_ints[street][raw_avenue] = (lat, lon)

    for street, ints in all_ints.items():
        for ave, ll in ints.items():
            all_ints_by_ave[ave][street] = ll

    return all_ints, all_ints_by_ave


def strip_dir(street: str) -> str:
    """Remove cardinal directions from street names."""
    return re.sub(r"\b(east|west|north|south)\b", "", street, flags=re.I).replace("()", "").strip()


def strip_ave(street: str) -> str:
    """Remove suffixes like Street, Avenue, etc."""
    return re.sub(
        r"\b(avenue|street|boulevard|place|road|drive|lane)\b", "", street, flags=re.I
    ).strip()


def load_all_intersections():
    # Completely unambiguous intersections
    ints = dict[Intersection, Point]()
    for row in csv.DictReader(open("data/nyc-intersections.csv")):
        # Street1,Street2,Borough,Lat,Lon,Nodes
        str1 = row["Street1"]
        str2 = row["Street2"]
        boro = row["Borough"]
        lat = float(row["Lat"])
        lng = float(row["Lon"])
        # nodes = tuple(int(x) for x in row["Nodes"].split("/"))
        ix = Intersection(str1, str2, boro)
        assert ix not in ints, ix
        ints[ix] = (lat, lng)

    # Intersections that are unambiguous after removing cardinal directions.
    stripped_pts = defaultdict[Intersection, set[Point]](set)
    for ix, pt in ints.items():
        s1 = strip_dir(ix.str1)
        s2 = strip_dir(ix.str2)
        if not strip_ave(s1) or not strip_ave(s2):
            continue  # Disallow, e.g., "South Street" -> "Street"
        k = Intersection(s1, s2, ix.boro)
        stripped_pts[k].add(pt)

    unambig_pts = {k: [*pt][0] for k, pt in stripped_pts.items() if len(pt) == 1}

    return ints, unambig_pts


AVE_TO_NUM = {"A": 0, "B": -1, "C": -2, "D": -3}


def ave_to_num(ave: str):
    if ave in AVE_TO_NUM:
        return AVE_TO_NUM[ave]
    else:
        return int(ave)


def correl(xs_list: Sequence[float | int], ys_list: Sequence[float | int]):
    xs = np.array(xs_list, dtype=float)
    ys = np.array(ys_list, dtype=float)
    meanx = xs.mean()
    meany = ys.mean()
    stdx = xs.std()
    stdy = ys.std()
    return ((xs * ys).mean() - meanx * meany) / (stdx * stdy)


def extract_lat_lons(num_to_lls):
    """Returns (xs, lats, lons) as parallel lists."""
    lats = sorted([(ave_to_num(x), num_to_lls[x][0]) for x in num_to_lls.keys()])
    lons = sorted([(ave_to_num(x), num_to_lls[x][1]) for x in num_to_lls.keys()])
    ns = [x[0] for x in lats]
    lats = [x[1] for x in lats]
    lons = [x[1] for x in lons]
    return ns, lats, lons


def correl_lat_lons(num_to_lls):
    """Measure how straight a street is.

    Given a dict mapping street/ave # --> (lat, lon), returns min(r^2).
    """
    xs, lats, lons = extract_lat_lons(num_to_lls)
    r_lat = correl(xs, lats)
    r_lon = correl(xs, lons)
    return min(r_lat * r_lat, r_lon * r_lon)


def get_line(num_to_lls):
    """Get the line (lat=a*lon+b) for a street or avenue.

    Returns (b, a), i.e. (intercept, slope)
    """
    ns, lats, lons = extract_lat_lons(num_to_lls)
    xs = np.zeros((len(lons), 2))
    xs[:, 0] = 1
    xs[:, 1] = lons
    ys = np.array(lats)
    return np.linalg.lstsq(xs, ys)[0]


def may_extrapolate(avenue: str, street: str):
    """Is this a valid intersection to extrapolate?"""
    ave_num = ave_to_num(avenue)
    str_num = int(street)

    # This cuts out the West Village and 4th Avenue south of 14th Street.
    # Streets are crooked there.
    # Valid intersections in those areas should be exact.
    if str_num <= 14 and ave_num > 2:
        return False
    # Avenues B, C and D should not extend above 23rd. They'd be underwater!
    elif str_num >= 23 and ave_num < 0:
        return False
    return True


class GridGeocoder:
    def __init__(self):
        # Manhattan from Houston to 125th Street, crossed by numbered/lettered avenues
        self.by_avenue, self.by_street = load_mini_grid()

        # Manhattan from Houston to 220th Street, with all north/south streets
        self.all_ints, self.all_ints_by_ave = load_manhattan_intersections()

        # All intersections, all five boroughs
        self.nyc_ints, self.stripped_nyc_ints = load_all_intersections()

        self.counts = Counter[str]()
        self.unknown_ave = Counter[str]()
        self.unknown_str = Counter[str]()

    def extrapolate_intersection(self, avenue: str, street: int):
        street_to_lls = self.by_avenue[avenue]
        ave_to_lls = self.by_street[street]

        if correl_lat_lons(street_to_lls) < 0.99 or correl_lat_lons(ave_to_lls) < 0.99:
            return None

        b_ave, a_ave = get_line(street_to_lls)
        b_str, a_str = get_line(ave_to_lls)

        lon = (b_ave - b_str) / (a_str - a_ave)
        lat = b_ave + lon * a_ave

        return lat, lon

    def code(self, avenue: str, street: str) -> tuple[float, float] | None:
        """Find the location of a current or historical intersection.

        `avenue` and `street` are strings, e.g. 'A' and '15'.
        Returns (lat, lon) or None.
        """
        crosses = self.by_avenue.get(avenue)
        if not crosses:
            self.unknown_ave[avenue] += 1
            self.counts["unclaimed"] += 1
            return None

        # First look for an exact match.
        exact = crosses.get(int(street))
        if exact:
            self.counts["exact_grid"] += 1
            return (exact[0], exact[1])

        # Otherwise, find where the street and avenue would logically intersect one
        # another if they continued as straight lines.
        street_crosses = self.by_street.get(int(street))
        if not street_crosses:
            self.unknown_str[street] += 1
            self.counts["unclaimed"] += 1
            return None

        if not may_extrapolate(avenue, street):
            sys.stderr.write("Rejecting extrapolation for %s, %s\n" % (avenue, street))
            return None

        self.counts["extrapolated"] += 1  # this might still fail
        return self.extrapolate_intersection(avenue, int(street))

    def geocode_intersection(
        self, street1: str, street2: str, boro: str, debug_txt: Optional[str] = ""
    ) -> Point | None:
        sys.stderr.write(f'Attempting to geocode "{street1}" and "{street2}"\n')

        street1 = normalize_street(street1)
        street2 = normalize_street(street2)
        ix = Intersection(street1, street2, boro)
        pt = self.nyc_ints.get(ix)
        if pt:
            self.counts["exact"] += 1
            return pt

        # Try stripping cardinal directions
        s1dir = strip_dir(street1)
        s2dir = strip_dir(street2)
        ixdir = Intersection(s1dir, s2dir, boro)
        pt = self.stripped_nyc_ints.get(ixdir)
        if pt:
            self.counts["dir strip"] += 1
            return pt

        if boro != "Manhattan":
            return None

        # If either looks like a numbered street, check for an exact match.
        num1 = extract_street_num(street1)
        if not num1:
            num2 = extract_street_num(street2)
            if num2:
                street1, street2 = street2, street1
                num1 = num2

        sys.stderr.write(f"{debug_txt} {street1} ({num1}) / {street2}\n")

        if num1:
            avenue = parse_ave_for_osm(street2)
            avenues = self.all_ints.get(num1)
            if avenues:
                latlng = avenues.get(avenue)
                if latlng:
                    self.counts["exact: str"] += 1
                    return latlng

            # There's no exact match, but we might be able to interpolate.
            ave_ints = self.all_ints_by_ave.get(avenue)
            if ave_ints:
                latlng = interpolate(ave_ints, num1)
                if latlng:
                    self.counts["interpolated"] += 1
                    sys.stderr.write(
                        f"{debug_txt} Interpolated {street2} ({avenue}) & {street1} ({num1}) to {latlng}\n"
                    )
                    return latlng

        # Either of these can raise a ValueError
        avenue, street = parse_street_ave(street1, street2)
        return self.code(avenue, street)

    def log_stats(self):
        sys.stderr.write("Grid statistics:\n")
        sys.stderr.write(f"           Counts: {self.counts.most_common()}\n")
        sys.stderr.write(f"  Unknown avenues: {self.unknown_ave}\n")
        sys.stderr.write(f"  Unknown streets: {self.unknown_str}\n")


singleton: GridGeocoder | None = None


def Grid():
    global singleton
    if not singleton:
        singleton = GridGeocoder()
    return singleton


ORDINALS = {
    "first": 1,
    "second": 2,
    "third": 3,
    "fourth": 4,
    "fifth": 5,
    "sixth": 6,
    "seventh": 7,
    "eighth": 8,
    "ninth": 9,
    "tenth": 10,
    "eleventh": 11,
    "twelfth": 12,
    "thirteenth": 13,
}
ordinals_re = re.compile(r"^(%s)\b" % "|".join(ORDINALS.keys()), flags=re.I)

NYC_ORDINALS = {
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
    "Thirteenth": 13,
    # Some NYC-specific stuff
    "Amsterdam": 10,
    "Park": 4,
    "Columbus": 9,
    "West End": 11,
    "Lenox": 6,  # Now Malcolm X
}
nyc_ave_re = re.compile(r"\b(%s) Ave(?:\.?|nue)\b" % "|".join(NYC_ORDINALS.keys()), flags=re.I)

NYC_NAMED_AVES = {
    "Adam Clayton Powell Jr. Boulevard": 7,
    "Malcolm X Boulevard": 6,
    "Frederick Douglass Boulevard": 8,
}

# "Avenues" that do not have "Avenue" in their names
SPECIAL_AVES = {
    "Broadway",
    "Central Park West",
    "St. Nicholas Avenue",
    "Saint Nicholas Avenue",
}


# See http://stackoverflow.com/a/20007730/388951
def make_ordinal(n):
    return "%d%s" % (n, "tsnrhtdd"[(n // 10 % 10 != 1) * (n % 10 < 4) * n % 10 :: 4])


def normalize_street(s: str) -> str:
    """Light normalization, e.g. "First Avenue" -> "1st Avenue"."""
    s = ordinals_re.sub(lambda m: make_ordinal(ORDINALS[m.group(1).lower()]), s)
    s = expand_abbrevs(s)
    return s


def expand_abbrevs(s: str) -> str:
    """Expand "Ave" -> "Avenue", "St" -> "Street", etc."""
    s = re.sub(r"St\.? Nicholas", "Saint Nicholas", s)
    s = re.sub(r"\bSt\.?(?= |$)", "Street", s)
    s = re.sub(r"\bAve\.?(?= |$)", "Avenue", s)
    s = re.sub(r"\bPl\.?(?= |$)", "Place", s)
    s = re.sub(r"\bDr\.?(?= |$)", "Drive", s)
    s = re.sub(r"\bRd\.?(?= |$)", "Road", s)
    s = re.sub(r"\bLn\.?(?= |$)", "Lane", s)
    s = re.sub(r"\bBlvd\.?(?= |$)", "Boulevard", s)
    s = re.sub(r"\bE\.?(?= |$)", "East", s)
    s = re.sub(r"\bW\.?(?= |$)", "West", s)
    s = re.sub(r"\bN\.?(?= |$)", "North", s)
    s = re.sub(r"\bS\.?(?= |$)", "South", s)
    return s


def parse_ave(avenue: str) -> str | None:
    """Normalize avenue names, e.g. "Fifth Avenue" -> "5"."""
    if avenue in SPECIAL_AVES:
        return avenue
    if avenue == "Riverside Park":
        return "Riverside Drive"
    num = extract_ordinal(avenue)
    if num is not None:
        return str(num)

    # Look for something like 'Avenue A'
    m = re.search(r"[aA]venue (A|B|C|D)", avenue)
    if m:
        return m.group(1)

    m = re.search(nyc_ave_re, avenue)
    if m:
        return str(NYC_ORDINALS[m.group(1)])

    # TODO: get rid of multisearch
    num = multisearch(NYC_NAMED_AVES, avenue)
    if num is not None:
        return str(num)


def parse_ave_for_osm(avenue: str) -> str:
    """Looser parsing, tries to match exact OSM names."""
    ave = parse_ave(avenue)
    if ave is not None:
        return ave
    avenue = avenue.replace("St. Nicholas", "Saint Nicholas")
    return avenue


def parse_street_ave(street1: str, street2: str) -> tuple[str, str]:
    # try to get the avenue in street1
    if re.search(r"str|st\.|\bst\b", street1, flags=re.I) and "Nicholas" not in street1:
        street2, street1 = street1, street2

    street1 = street1.replace("Central Park West", "8th Avenue")

    if not re.search(r"ave", street1, flags=re.I) and street1 not in SPECIAL_AVES:
        raise ValueError("%s is not an avenue" % street1)

    if not re.search(r"str|st\.|\bst\b", street2, flags=re.I):
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
    ave = parse_ave(street1)
    if ave is None:
        raise ValueError("Did not find an avenue in %s" % street1)

    return ave, street2


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


def text_to_number(text: str) -> int | None:
    # Normalize the text
    text = text.lower().strip()

    # Define ordinal mappings
    ordinal_mapping = {
        "first": 1,
        "second": 2,
        "third": 3,
        "fourth": 4,
        "fifth": 5,
        "sixth": 6,
        "seventh": 7,
        "eighth": 8,
        "ninth": 9,
        "tenth": 10,
        "eleventh": 11,
        "twelfth": 12,
        "thirteenth": 13,
        "fourteenth": 14,
        "fifteenth": 15,
        "sixteenth": 16,
        "seventeenth": 17,
        "eighteenth": 18,
        "nineteenth": 19,
        "twentieth": 20,
        "thirtieth": 30,
        "fortieth": 40,
        "fiftieth": 50,
        "sixtieth": 60,
        "seventieth": 70,
        "eightieth": 80,
        "ninetieth": 90,
        "hundredth": 100,
        "thousandth": 1000,
    }

    # Handle simple ordinals
    for word, number in ordinal_mapping.items():
        if text.endswith(word):
            base_text = text[: -len(word)].strip()
            try:
                base_number = w2n.word_to_num(base_text) if base_text else 0
                if not isinstance(base_number, int):
                    return None
                return base_number + number
            except ValueError:
                return number if not base_text else None

    # Attempt to parse as a cardinal number
    try:
        x = w2n.word_to_num(text)
        if not isinstance(x, int):
            return None
    except ValueError:
        return None


def extract_street_num(street: str) -> int | None:
    m = re.search(r"\b(?<!-)(\d+)(?:st|nd|rd|th) (?:Street|St\.|St\b)", street, flags=re.I)
    if m:
        return int(m.group(1))
    # try for an ordinal
    m = re.search(r"(.*?) (?:Street|St\.|St\b)", street, flags=re.I)
    if not m:
        return None
    return text_to_number(m.group(1))


def interpolate(ave_ints: dict[int, Point], num: int) -> Point | None:
    t0, pt0, t1, pt1 = None, None, None, None
    for dm in range(1, 3):
        t0 = num - dm
        pt0 = ave_ints.get(t0)
        if pt0:
            break

    if t0 is None or pt0 is None:
        return None

    for dp in range(1, 3):
        t1 = num + dp
        pt1 = ave_ints.get(t1)
        if pt1:
            break

    if t1 is None or pt1 is None:
        return None

    # Interpolate between the two points.
    frac = (num - t0) / (t1 - t0)
    lat = pt0[0] + frac * (pt1[0] - pt0[0])
    lng = pt0[1] + frac * (pt1[1] - pt0[1])
    # print(f"Interpolating between {t0} and {t1} for {num}")
    return lat, lng


if __name__ == "__main__":
    g = Grid()
    print("Avenues and streets with imperfect correlations:")
    print("Avenues:")
    for ave in sorted(g.by_avenue.keys()):
        r2 = correl_lat_lons(g.by_avenue[ave])
        if r2 < 0.99:
            print("  %3s: %s" % (ave, r2))

    print("Streets:")
    for street in sorted(g.by_street.keys()):
        r2 = correl_lat_lons(g.by_street[street])
        if r2 < 0.99:
            print("  %3s: %s" % (street, r2))
