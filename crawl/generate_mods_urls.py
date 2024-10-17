#!/usr/bin/env python

from oldnyc.item import load_items

MODS_URL = "https://api.repo.nypl.org/api/v2/mods/%s"

if __name__ == "__main__":
    for item in load_items("data/images.ndjson"):
        # if not item.back_id:
        #     continue
        mods_url = MODS_URL % item.uuid
        print(f"{mods_url}\t{item.id}.json")
