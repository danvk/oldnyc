"""Generate intersections.csv by looking for Avenue/Street intersections in an OSM dump."""

import csv
import itertools
import json
import re
import sys
from collections import Counter, defaultdict
from typing import Sequence

from haversine import haversine
from tqdm import tqdm

from oldnyc.geocode.boroughs import is_in_manhattan, point_to_borough
from oldnyc.geocode.osm.osm import OsmElement, OsmNode, OsmWay


def load_osm_data() -> list[OsmElement]:
    osm_data = json.load(open("data/osm-roads.json"))
    els = osm_data["elements"]
    return els


AVE_TO_NUM = {"A": 0, "B": -1, "C": -2, "D": -3}


def interpret_as_ave(w: OsmWay) -> str | None:
    name = w["tags"].get("name")
    alt_name = w["tags"].get("alt_name")
    if "Street" in (name or "") or "Bridge" in (name or ""):
        # filter out, e.g. "East 125th Street" = "Dr. MLK Jr. Blvd"
        # or "Madison Avenue Bridge"
        return None
    names = [x for x in [name, alt_name] if x is not None]
    for name in names:
        if (
            "Avenue" in name
            or "Boulevard" in name
            or "Broadway" in name
            or "Central Park West" in name
            or "Sutton Place" in name
            or "Riverside Drive" in name
        ):
            return name


def interpret_as_street(w: OsmWay) -> int | None:
    name = w["tags"].get("name")
    alt_name = w["tags"].get("alt_name")

    names = [x for x in [name, alt_name] if x is not None]
    for name in names:
        name = name.replace("Street", "").strip()
        name = re.sub(r"\b(east|west)\b", "", name, flags=re.I).strip()
        name = re.sub(r"\b(\d+)(?:st|nd|rd|th)\b", r"\1", name).strip()

        try:
            base_num = int(name)
        except ValueError:
            continue
        return base_num


# See http://stackoverflow.com/a/20007730/388951
def make_ordinal(n):
    return "%d%s" % (n, "tsnrhtdd"[(n // 10 % 10 != 1) * (n % 10 < 4) * n % 10 :: 4])


def make_avenue_str(avenue, street=0) -> str | None:
    """1 --> 1st Avenue, -1 --> Avenue B"""
    if avenue <= 0:
        return "Avenue " + ["A", "B", "C", "D"][-avenue]
    elif avenue == 4:
        if 17 <= street <= 32:
            return "Park Avenue South"
        elif street > 32:
            return "Park Avenue"
        else:
            return None
    elif avenue == 6 and street >= 110:
        return "Malcolm X Boulevard"
    elif avenue == 7 and street >= 110:
        return "Adam Clayton Powell Jr. Boulevard"
    elif avenue == 8 and 59 <= street <= 110:
        return "Central Park West"
    elif avenue == 8 and street > 110:
        return "Frederick Douglass Boulevard"
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


def get_intersection_center(nodes: Sequence[OsmNode]) -> tuple[float, float]:
    # If there are multiple nodes, it's likely they're the sides or corners of the
    # intersection. It's fine to average them, after a sanity check.
    for a, b in itertools.combinations(nodes, 2):
        d = haversine((a["lat"], a["lon"]), (b["lat"], b["lon"])) * 1000
        # Riverside Drive / 110: 42452276 <-> 42441926 111m
        if d > 120:
            sys.stderr.write(f"  {a['id']} <-> {b['id']} {d:.0f}m\n")
            raise ValueError("Ambiguous intersection")

    num = len(nodes)
    return (
        sum(n["lat"] for n in nodes) / num,
        sum(n["lon"] for n in nodes) / num,
    )


def main():
    els = load_osm_data()
    ways = [
        el
        for el in els
        if el["type"] == "way" and el["tags"].get("name") and el["tags"].get("highway") != "footway"
    ]

    id_to_way = {el["id"]: el for el in ways}
    all_nodes = [el for el in els if el["type"] == "node"]
    id_to_node = {el["id"]: el for el in all_nodes}

    assert 1250608533 in id_to_way
    assert 848013829 in id_to_way
    assert 1025731531 in id_to_way

    assert 848013829 in id_to_way  # Amsterdam Avenue
    assert 5671540 in id_to_way  # West 104th Street

    node_counts = Counter[int]()
    for way in ways:
        for node in set(way["nodes"]):
            node_counts[node] += 1
    intersection_nodes = [n for n, v in node_counts.items() if v >= 2]

    node_to_ways = defaultdict(list)
    int_set = set(intersection_nodes)
    for way in ways:
        for node in way["nodes"]:
            if node in int_set:
                node_to_ways[node].append(way["id"])

    # Exclude self-intersections, e.g. W 106th St. is split into multiple ways.
    intersection_nodes = [
        n
        for n in intersection_nodes
        if len(set(id_to_way[w]["tags"]["name"] for w in node_to_ways[n])) >= 2
    ]

    print(set(id_to_way[w]["tags"]["name"] for w in node_to_ways[42952845]))
    assert 42952845 not in intersection_nodes
    assert 42442559 in intersection_nodes
    assert 42442561 in intersection_nodes

    way_pairs = defaultdict[tuple[str, str], set[int]](set)
    for node in intersection_nodes:
        ways = node_to_ways[node]
        for a, b in itertools.combinations(ways, 2):
            if a == b:
                continue  # can be a self-intersection, e.g. a loop
            wa = id_to_way[a]
            wb = id_to_way[b]
            name_a = wa["tags"]["name"]
            name_b = wb["tags"]["name"]
            if name_a == name_b:
                continue
            way_pairs[tuple(sorted((name_a, name_b)))].add(node)

    claimed_nodes = set[int]()
    with open("data/nyc-intersections.csv", "w") as f:
        out = csv.writer(f)
        out.writerow(["Street1", "Street2", "Borough", "Lat", "Lon", "Nodes"])
        for (str1, str2), intersect_node_ids in tqdm(sorted(way_pairs.items())):
            if all(n in claimed_nodes for n in intersect_node_ids):
                continue
            try:
                intersect_nodes = [id_to_node[n] for n in intersect_node_ids]
            except KeyError:
                print("Missing intersection node", str1, str2)
                raise
            try:
                lat, lng = get_intersection_center(intersect_nodes)
            except ValueError:
                print(f"Ambiguous intersection: {str1} / {str2}: ({intersect_node_ids})")
                continue
            # claimed_nodes.update(intersect_node_ids)
            borough = point_to_borough(lat, lng)
            if borough is None:
                print(f"Not in NYC: {str1} / {str2}: ({intersect_node_ids})")
                continue
            out.writerow(
                [
                    str(str1),
                    str(str2),
                    borough,
                    str(round(lat, 6)),
                    str(round(lng, 6)),
                    "/".join(str(n) for n in intersect_node_ids),
                ]
            )


if __name__ == "__main__":
    main()
