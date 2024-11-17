"""Generate intersections.csv by looking for Avenue/Street intersections in an OSM dump."""

import itertools
import json
import re
import sys
from collections import Counter, defaultdict
from typing import TypeVar

from haversine import haversine
from tqdm import tqdm

from oldnyc.geocode.boroughs import is_in_manhattan
from oldnyc.geocode.osm.osm import OsmElement, OsmWay


def load_osm_data() -> list[OsmElement]:
    osm_data = json.load(open("data/osm-roads.json"))
    els = osm_data["elements"]
    return els


AVE_TO_NUM = {"A": 0, "B": -1, "C": -2, "D": -3}


T = TypeVar("T")
V = TypeVar("V")


def invert(d: dict[T, set[V]]) -> dict[V, set[T]]:
    out = defaultdict(set)
    for k, vs in d.items():
        for v in vs:
            out[v].add(k)
    return out


def interpret_as_ave(w: OsmWay) -> str | None:
    name = w["tags"].get("name")
    alt_name = w["tags"].get("alt_name")
    names = [x for x in [name, alt_name] if x is not None]
    for name in names:
        if (
            "Avenue" in name
            or "Boulevard" in name
            or "Broadway" in name
            or "Central Park West" in name
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

    manhattan_intersections = [
        n
        for n in tqdm(intersection_nodes)
        if is_in_manhattan(id_to_node[n]["lat"], id_to_node[n]["lon"])
    ]

    node_to_ways = defaultdict(list)
    int_set = set(intersection_nodes)
    for way in ways:
        for node in way["nodes"]:
            if node in int_set:
                node_to_ways[node].append(way["id"])

    # Exclude self-intersections, e.g. W 106th St. is split into multiple ways.
    manhattan_intersections = [
        n
        for n in manhattan_intersections
        if len(set(id_to_way[w]["tags"]["name"] for w in node_to_ways[n])) >= 2
    ]

    assert 42442559 in manhattan_intersections
    assert 42442561 in manhattan_intersections

    manhattan_roads = [
        id_to_way[w] for w in {w for int_n in manhattan_intersections for w in node_to_ways[int_n]}
    ]

    ave_a = [m for m in manhattan_roads if m["id"] == 195743554]
    assert ave_a

    street_num_to_ways = defaultdict[int, set[int]](set)
    ave_num_to_ways = defaultdict[str, set[int]](set)
    for w in manhattan_roads:
        ave_name = interpret_as_ave(w)
        if ave_name:
            ave_num_to_ways[ave_name].add(w["id"])
            continue

        street_num = interpret_as_street(w)
        if street_num is not None:
            street_num_to_ways[street_num].add(w["id"])

    street_to_nodes = {
        k: {n for way_id in way_ids for n in id_to_way[way_id]["nodes"]}
        for k, way_ids in street_num_to_ways.items()
    }
    ave_to_nodes = {
        k: {n for way_id in way_ids for n in id_to_way[way_id]["nodes"]}
        for k, way_ids in ave_num_to_ways.items()
    }
    # node_to_street = invert(street_to_nodes)
    # node_to_ave = invert(ave_to_nodes)

    # This might be a more useful format than intersections.csv.
    # It's more "raw" and matches the street names more directly.
    # for ave in sorted(ave_to_nodes.keys()):
    #     nodes = ave_to_nodes[ave]
    #     for node in nodes:
    #         lat = id_to_node[node]["lat"]
    #         lon = id_to_node[node]["lon"]
    #         streets = node_to_street.get(node)
    #         for street in sorted(streets or []):
    #             print(f"{ave}\t{street}\t{node}\t{lat},{lon}")

    def locate(ave: int, street: int) -> tuple[float, float] | None:
        street_nodes = street_to_nodes.get(street)
        if not street_nodes:
            return None
        ave_str = make_avenue_str(ave, street)
        if ave_str is None:
            return None
        ave_nodes = ave_to_nodes.get(ave_str)
        if not ave_nodes:
            return None

        intersect_node_ids = street_nodes & ave_nodes
        if not intersect_node_ids:
            return None
        intersect_nodes = [id_to_node[n] for n in intersect_node_ids]

        # If there are multiple nodes, it's likely they're the sides or corners of the
        # intersection. It's fine to average them, after a sanity check.
        for a, b in itertools.combinations(intersect_nodes, 2):
            d = haversine((a["lat"], a["lon"]), (b["lat"], b["lon"])) * 1000
            if d > 100:
                sys.stderr.write(f"  {a['id']} <-> {b['id']} {d:.0f}m\n")
                raise ValueError("Ambiguous intersection")

        num = len(intersect_nodes)
        return (
            round(sum(n["lat"] for n in intersect_nodes) / num, 6),
            round(sum(n["lon"] for n in intersect_nodes) / num, 6),
        )

    crosses: list[tuple[int, int]] = []
    for street in range(1, 125):
        for ave in range(-3, 13 if street >= 14 else 7):
            crosses.append((ave, street))

    rows = [["Street", "Avenue", "Lat", "Lon"]]
    for i, (ave, street) in enumerate(crosses):
        lat, lon = locate(ave, street) or ("", "")
        if (ave, street, lat, lon) == (11, 14, "", ""):
            # Google geocodes this one but OSM has 14th street end at 10th Ave.
            # The correct behavior is debatable, but this lets us keep a few photos.
            lat, lon = (40.7424762, -74.0088873)
        rows.append([str(x) for x in [street, ave, lat, lon]])

    delim = ","
    for row in rows:
        print(delim.join(row))


if __name__ == "__main__":
    main()
