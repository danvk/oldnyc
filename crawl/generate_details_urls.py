#!/usr/bin/env python

import json

from data.item import Item

DETAILS_URL = "https://api.repo.nypl.org/api/v2/items/item_details/%s"

if __name__ == "__main__":
    for line in open("data/images.ndjson"):
        item = Item(**json.loads(line))
        if item.id.endswith("f"):
            continue
        url = DETAILS_URL % item.uuid
        print(f"{url}\t{item.id}.json")
