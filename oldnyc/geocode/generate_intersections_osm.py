"""Generate intersections.csv by looking for Avenue/Street intersections in an OSM dump."""

import json
from collections import Counter, defaultdict

from tqdm import tqdm

from oldnyc.geocode.boroughs import is_in_manhattan
from oldnyc.geocode.osm import OsmElement


def load_osm_data() -> list[OsmElement]:
    osm_data = json.load(open("/Users/danvk/github/computing-in-the-catskills/data/nyc-roads.json"))
    els = osm_data["elements"]
    return els


def main():
    els = load_osm_data()
    ways = [el for el in els if el["type"] == "way" and el["tags"].get("name")]

    id_to_way = {el["id"]: el for el in ways}
    all_nodes = [el for el in els if el["type"] == "node"]
    id_to_node = {el["id"]: el for el in all_nodes}
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

    print(f"{len(ways)=}")
    print(f"{len(manhattan_intersections)=}")

    print(manhattan_intersections[0])
    print([id_to_way[w] for w in node_to_ways[manhattan_intersections[0]]])


if __name__ == "__main__":
    main()
