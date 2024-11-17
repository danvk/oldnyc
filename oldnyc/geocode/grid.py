#!/usr/bin/env python

import csv
import re
import sys
from collections import Counter, defaultdict
from typing import Sequence

import numpy as np
from pygeojson import Optional

Point = tuple[float, float]

# These are just the Manhattan grid intersections (from Houston to 125th)
by_avenue = defaultdict[str, dict[int, Point]](lambda: {})
by_street = defaultdict[int, dict[str, Point]](lambda: {})

# These are all intersections in Manhattan, not just the grid.
all_ints = defaultdict[int, dict[str, Point]](lambda: {})
all_ints_by_ave = defaultdict[str, dict[int, Point]](lambda: {})

is_initialized = False


def load_data():
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
        by_avenue[avenue][street] = (lat, lon)
        by_street[street][avenue] = (lat, lon)

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

    global is_initialized
    is_initialized = True


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


def extrapolate_intersection(avenue: str, street: int):
    if not is_initialized:
        load_data()
    street_to_lls = by_avenue[avenue]
    ave_to_lls = by_street[street]

    if correl_lat_lons(street_to_lls) < 0.99 or correl_lat_lons(ave_to_lls) < 0.99:
        return None

    b_ave, a_ave = get_line(street_to_lls)
    b_str, a_str = get_line(ave_to_lls)

    lon = (b_ave - b_str) / (a_str - a_ave)
    lat = b_ave + lon * a_ave

    return lat, lon


def may_extrapolate(avenue: str, street: str):
    """Is this a valid intersection to extrapolate?"""
    if not is_initialized:
        load_data()
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


num_exact = 0
num_exact_grid = 0
num_unclaimed = 0
num_extrapolated = 0
unknown_ave = Counter[str]()
unknown_str = Counter[str]()


def code(avenue: str, street: str) -> tuple[float, float] | None:
    """Find the location of a current or historical intersection.

    `avenue` and `street` are strings, e.g. 'A' and '15'.
    Returns (lat, lon) or None.
    """
    if not is_initialized:
        load_data()
    global num_exact, num_unclaimed, num_extrapolated, num_exact_grid

    crosses = by_avenue.get(avenue)
    if not crosses:
        unknown_ave[avenue] += 1
        num_unclaimed += 1
        return None

    # First look for an exact match.
    exact = crosses.get(int(street))
    if exact:
        num_exact_grid += 1
        return (exact[0], exact[1])

    # Otherwise, find where the street and avenue would logically intersect one
    # another if they continued as straight lines.
    street_crosses = by_street.get(int(street))
    if not street_crosses:
        unknown_str[street] += 1
        num_unclaimed += 1
        return None

    if not may_extrapolate(avenue, street):
        sys.stderr.write("Rejecting extrapolation for %s, %s\n" % (avenue, street))
        return None

    num_extrapolated += 1
    return extrapolate_intersection(avenue, int(street))


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
    "Adam Clayton Powell Jr. Boulevard": 7,
    "Malcolm X Boulevard": 6,
    "Frederick Douglass Boulevard": 8,
}

# "Avenues" that do not have "Avenue" in their names
SPECIAL_AVES = {
    "Broadway",
    "Central Park West",
}


def parse_ave(avenue: str) -> str | None:
    """Normalize avenue names, e.g. "Fifth Avenue" -> "5"."""
    if avenue in SPECIAL_AVES:
        return avenue
    num = extract_ordinal(avenue)
    if num is not None:
        return str(num)

    # Look for something like 'Avenue A'
    m = re.search(r"[aA]venue (A|B|C|D)", avenue)
    if m:
        return m.group(1)
    else:
        # How about 'Fourth', 'Fifth'?
        num = multisearch(ORDINALS, avenue)
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
    if re.search(r"str|st\.|\bst\b", street1, flags=re.I):
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


def extract_street_num(street: str) -> int | None:
    name = street.replace("Street", "").strip()
    name = re.sub(r"\b(east|west)\b", "", name, flags=re.I).strip()
    name = name.replace("()", "")  # remains of "(east)" or "(west)"
    name = re.sub(r"\b(\d+)(?:st|nd|rd|th)\b", r"\1", name).strip()

    try:
        base_num = int(name)
    except ValueError:
        return None
    return base_num


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


def geocode_intersection(street1: str, street2: str, debug_txt: Optional[str] = "") -> Point | None:
    if not is_initialized:
        load_data()
    global num_exact

    # If either looks like a numbered street, check for an exact match.
    num1 = extract_street_num(street1)
    if not num1:
        num2 = extract_street_num(street2)
        if num2:
            street1, street2 = street2, street1
            num1 = num2
    if num1:
        avenue = parse_ave_for_osm(street2)
        avenues = all_ints.get(num1)
        if avenues:
            latlng = avenues.get(avenue)
            if latlng:
                num_exact += 1
                return latlng
            sys.stderr.write(f"Miss on intersection: {debug_txt} {num1}, {street2} -> {avenue}\n")

        # There's no exact match, but we might be able to interpolate.
        ave_ints = all_ints_by_ave.get(avenue)
        if ave_ints:
            latlng = interpolate(ave_ints, num1)
            if latlng:
                return latlng

    # Either of these can raise a ValueError
    avenue, street = parse_street_ave(street1, street2)
    return code(avenue, street)


def log_stats():
    sys.stderr.write("Grid statistics:\n")
    sys.stderr.write(f"     Exact matches: {num_exact}\n")
    sys.stderr.write(f"Exact grid matches: {num_exact_grid}\n")
    sys.stderr.write(f"      Extrapolated: {num_extrapolated}\n")
    sys.stderr.write(f"         Unclaimed: {num_unclaimed}\n")
    sys.stderr.write(f"   Unknown avenues: {unknown_ave}\n")
    sys.stderr.write(f"   Unknown streets: {unknown_str}\n")


if __name__ == "__main__":
    load_data()
    print("Avenues and streets with imperfect correlations:")
    print("Avenues:")
    for ave in sorted(by_avenue.keys()):
        r2 = correl_lat_lons(by_avenue[ave])
        if r2 < 0.99:
            print("  %3s: %s" % (ave, r2))

    print("Streets:")
    for street in sorted(by_street.keys()):
        r2 = correl_lat_lons(by_street[street])
        if r2 < 0.99:
            print("  %3s: %s" % (street, r2))
