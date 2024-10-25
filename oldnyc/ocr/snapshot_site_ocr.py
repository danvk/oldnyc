#!/usr/bin/env python
"""Capture a snapshot of the OCR as it exists on the web site."""

import json

from oldnyc.item import load_items
from oldnyc.site.site_data_type import SiteJson


def main():
    items = load_items("data/images.ndjson")
    front_to_back = {r.id: r.back_id for r in items if r.back_id}

    site_data: SiteJson = json.load(open("../oldnyc.github.io/data.json"))
    site_text: dict[str, str] = {}
    back_to_photo_id = dict[str, str]()
    for photo in site_data["photos"]:
        id = photo["photo_id"].split("-")[0]
        back_id = front_to_back.get(id)
        if back_id and photo["text"]:
            site_text[back_id] = photo["text"]
            back_to_photo_id[back_id] = photo["photo_id"]

    print(json.dumps(site_text, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
