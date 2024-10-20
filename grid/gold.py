#!/usr/bin/env python
"""Generate intersections.csv by searching for every (avenue, street) pair.

This seems to have worked in 2015, but it's not working now. The Google Maps geocoder
seems to have gotten more aggressive about correcting non-existent intersections like
1st street and 5th avenue to 5th street and 1st avenue, or finding a matching
intersection in an entirely different county.
"""

import argparse
import json
import os
import sys

from dotenv import load_dotenv

from nyc.boroughs import PointToBorough
from oldnyc.geocode import geocoder


# See http://stackoverflow.com/a/20007730/388951
def make_ordinal(n):
    return "%d%s" % (n, "tsnrhtdd"[(n // 10 % 10 != 1) * (n % 10 < 4) * n % 10 :: 4])


def make_street_str(street, avenue):
    """1 -> 1st Street"""
    side = "East" if avenue <= 5 else "West"
    ordinal = make_ordinal(street)
    return f"{side} {ordinal} street"


def make_avenue_str(avenue, street=0):
    """1 --> 1st Avenue, -1 --> Avenue B"""
    if avenue <= 0:
        return "Avenue " + ["A", "B", "C", "D"][-avenue]
    elif avenue == 4:
        if 17 <= street <= 32:
            return "Park Avenue South"
        elif street > 32:
            return "Park Avenue"
    elif avenue == 6 and street >= 110:
        return "Malcolm X Blvd"
    elif avenue == 7 and street >= 110:
        return "Adam Clayton Powell Jr Blvd"
    elif avenue == 8 and 59 <= street <= 110:
        return "Central Park West"
    elif avenue == 8 and street > 110:
        return "Frederick Douglass Blvd"
    elif avenue == 10 and street >= 59:
        return "Amsterdam Avenue"
    elif avenue == 11 and street >= 59:
        return "West End Avenue"
    else:
        return make_ordinal(avenue) + " Avenue"


"""
10th Avenue --> Amsterdam Ave above 59th street
11th Avenue --> West End Ave above 59th street
 8th Avenue --> Central Park West from 59th to 110th
 8th Avenue --> Frederick Douglass Blvd above 110th
 7th Avenue --> Adam Clayton Powell Jr Blvd above 110th
 6th Avenue --> Malcolm X Blvd above 110th
 4th Avenue --> Park Avenue S from 17th to 32nd street
 4th Avenue --> Park Avenue above 32nd street
"""


def locate(avenue, street, verbose=False):
    """Avenue & Street are numbers. Returns (lat, lon). Avenue A is -1."""
    street_str = make_street_str(street, avenue)
    avenue_str = make_avenue_str(avenue, street)
    if avenue_str is None:
        return None
    location_str = "%s & %s, Manhattan, NY" % (street_str, avenue_str)
    print(location_str)
    response = g.Locate(location_str)
    if not response:
        return None

    # print(response)
    r = response["results"][0]
    if r["types"] != ["intersection"]:
        return None
    if r.get("partial_match"):
        return None  # may be inaccurate
    if verbose:
        print(json.dumps(r, indent=2))
    # r["address_components"][0]["long_name"]  # 1st Avenue & East 5th Street
    comp = r["address_components"][0]
    if "intersection" not in comp["types"]:
        return None
    long_name = comp["long_name"]
    if (street_str.lower() not in long_name.lower()) or (
        avenue_str.lower() not in long_name.lower()
    ):
        if verbose:
            sys.stderr.write(f"Discarding possible mismatch:\n-{location_str}\n+{long_name}\n")
        return None

    loc = r["geometry"]["location"]
    lat_lon = loc["lat"], loc["lng"]
    if PointToBorough(*lat_lon) != "Manhattan":
        if verbose:
            sys.stderr.write("Discarding non-Manhattan location\n")
        return None

    return lat_lon


if __name__ == "__main__":
    load_dotenv()
    parser = argparse.ArgumentParser(description="Generate coordinates of Manhattan intersections.")
    parser.add_argument(
        "-n",
        "--use_network",
        action="store_true",
        help="Set this to make the geocoder use the network. The "
        "alternative is to use only the geocache.",
    )
    parser.add_argument(
        "--format",
        choices=("tsv", "csv"),
        default="csv",
        help="Output format; tsv is useful for loading into a spreadsheet.",
    )
    parser.add_argument("--verbose", action="store_true", help="Print out progress messages.")
    args = parser.parse_args()
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    assert api_key
    g = geocoder.Geocoder(args.use_network, 2, api_key)  # use network, 1s wait time.

    crosses = []
    for street in range(1, 125):
        for ave in range(-3, 13 if street >= 14 else 7):
            crosses.append((ave, street))
    # crosses = [(5, 50)]
    # crosses = [(5, 1)]
    # crosses = [(6, 1)]
    crosses = [(2, 2)]
    # for street in range(1, 14):
    #     for ave in range(-3, 7):
    #         crosses.append((ave, street))
    # random.shuffle(crosses)

    rows = [["Street", "Avenue", "Lat", "Lon"]]
    for i, (ave, street) in enumerate(crosses):
        lat, lon = locate(ave, street, args.verbose) or ("", "")
        rows.append([str(x) for x in [street, ave, lat, lon]])
        if args.verbose:
            sys.stderr.write(
                "%d / %d --> %s / %s --> %s, %s\n"
                % (
                    1 + i,
                    len(crosses),
                    make_street_str(street, ave),
                    make_avenue_str(ave, street),
                    lat,
                    lon,
                )
            )

    delim = "," if args.format == "csv" else "\t"
    for row in rows:
        print(delim.join(row))
