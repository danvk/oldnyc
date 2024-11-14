#!/usr/bin/env python
"""Collect NYPL API data (mods, item_details) into a more manageable format."""

import json
import sys
from pathlib import Path


def as_list(dict_or_list: dict | list) -> list:
    return [dict_or_list] if isinstance(dict_or_list, dict) else dict_or_list


def is_photographer(name: dict):
    # Photographer, Artist, Lithographer, Creator
    return any(rt["$"] in ("pht", "art", "ltg", "cre") for rt in name["role"]["roleTerm"])


def extract_date(origin_info: dict | list) -> str | None:
    origins = as_list(origin_info)
    for origin in origins:
        for field in ("dateIssued", "dateCreated"):
            date = origin.get(field)
            if date:
                return ", ".join([d["$"] for d in as_list(date)])


if __name__ == "__main__":
    mods_dir, item_details_dir = sys.argv[1:]

    mapping = {}
    for p in Path(mods_dir).iterdir():
        data = json.load(open(p))
        nypl = data["nyplAPI"]
        req = nypl["request"]
        uuid = req["uuid"]["$"]

        resp = nypl["response"]
        assert resp["headers"]["status"]["$"] == "success"

        if resp.get("$") == "No Results Found":
            sys.stderr.write(f"Missing mods for {uuid}, skipping\n")
            continue

        mods = resp["mods"]
        titles = as_list(mods["titleInfo"])
        assert titles[0]["usage"] == "primary"
        title_strs = [t["title"]["$"] for t in titles]

        # TODO: output as a list
        names = as_list(mods.get("name", []))
        creators = [name["namePart"]["$"] for name in names if is_photographer(name)]
        creator = ";".join(creators) if creators else None

        origin = mods.get("originInfo")
        date = extract_date(origin) if origin else None

        sources = []
        relatedItem = mods["relatedItem"]
        while relatedItem:
            assert relatedItem["type"] == "host"
            sources = [relatedItem["titleInfo"]["title"]["$"]] + sources
            relatedItem = relatedItem.get("relatedItem")

        mapping[uuid] = {"titles": title_strs, "creator": creator, "sources": sources, "date": date}

    # 104425.json: no back image
    # 1552839.json: has back image

    for p in Path(item_details_dir).iterdir():
        data = json.load(open(p))
        nypl = data["nyplAPI"]
        req = nypl["request"]
        uuid = req["uuid"]["$"]

        resp = nypl["response"]
        assert resp["headers"]["status"]["$"] == "success"

        if "sibling_captures" not in resp or "capture" not in resp["sibling_captures"]:
            sys.stderr.write(f"{uuid} has no sibling captures.\n")
            continue
        sibs = as_list(resp["sibling_captures"]["capture"])

        if len(sibs) > 1:
            # the sibling capture is almost certainly a backing image.
            mapping.setdefault(uuid, {})
            mapping[uuid]["back_id"] = sibs[1]["imageID"]["$"]
        if len(sibs) > 2:
            sys.stderr.write(f"{uuid} has more than 2 siblings.\n")

    print(json.dumps(mapping, indent=2, sort_keys=True))
