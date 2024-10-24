#!/usr/bin/env python
"""Which is better, on-site OCR or GPT?"""

import json

from oldnyc.item import load_items
from oldnyc.site.site_data_type import SiteJson


def main():
    items = load_items("data/images.ndjson")
    front_to_back = {r.id: r.back_id for r in items if r.back_id}

    site_data: SiteJson = json.load(open("../oldnyc.github.io/data.json"))
    site_text: dict[str, str] = {}
    for photo in site_data["photos"]:
        id = photo["photo_id"].split("-")[0]
        back_id = front_to_back.get(id)
        if back_id and photo["text"]:
            site_text[back_id] = photo["text"]

    gpt_text: dict[str, str] = {
        id: r["text"]
        for id, r in json.load(open("data/gpt-ocr.json")).items()
        if r["text"] != "(rotated)"
    }

    n_int = sum(1 for id in site_text if id in gpt_text)
    print("n_site=", len(site_text))
    print("n_gpt=", len(gpt_text))
    print(f"{n_int=}")


if __name__ == "__main__":
    main()
