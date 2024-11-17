"""The Overpass results are a bit large to store in the repo.

This filters them down to just the ways/nodes that have names.
"""

import json
from collections import Counter

osm_data = json.load(
    open("/Users/danvk/github/computing-in-the-catskills/data/nyc-named-roads.json")
)
# Remove NYC relation
osm_data["elements"] = [el for el in osm_data["elements"] if el["type"] != "relation"]

node_counts = Counter[int]()
for el in osm_data["elements"]:
    if el["type"] != "way":
        continue
    new_tags = {}
    for k, v in el["tags"].items():
        if k in ("name", "alt_name", "highway"):
            new_tags[k] = v
    el["tags"] = new_tags

    for node in el["nodes"]:
        node_counts[node] += 1

osm_data["elements"] = [
    el for el in osm_data["elements"] if el["type"] == "way" or node_counts[el["id"]] > 1
]

print(json.dumps(osm_data, indent=None, separators=(",", ":")))
