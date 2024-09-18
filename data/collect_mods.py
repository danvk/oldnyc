#!/usr/bin/env python
"""Collect MODS data into a more manageable format."""

import json
from pathlib import Path
import sys


def as_list(dict_or_list: dict | list) -> list:
    return [dict_or_list] if isinstance(dict_or_list, dict) else dict_or_list


if __name__ == "__main__":
    mods_dir = sys.argv[1]
    mapping = {}
    for p in Path(mods_dir).iterdir():
        data = json.load(open(p))
        nypl = data["nyplAPI"]
        req = nypl["request"]
        uuid = req["uuid"]["$"]

        resp = nypl["response"]
        assert resp["headers"]["status"]["$"] == "success"

        mods = resp["mods"]
        titles = as_list(mods["titleInfo"])
        assert titles[0]["usage"] == "primary"

        title_strs = [t["title"]["$"] for t in titles]
        mapping[uuid] = title_strs

    print(json.dumps(mapping, indent=2, sort_keys=True))
