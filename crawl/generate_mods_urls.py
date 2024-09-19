#!/usr/bin/env python

import json

from data.item import Item

MODS_URL = "https://api.repo.nypl.org/api/v2/mods/%s"

if __name__ == "__main__":
    for line in open("data/images.ndjson"):
        item = Item(**json.loads(line))
        # if not item.back_id:
        #     continue
        mods_url = MODS_URL % item.uuid
        print(f"{mods_url}\t{item.id}.json")
