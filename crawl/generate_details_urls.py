#!/usr/bin/env python

from oldnyc.item import load_items

DETAILS_URL = "https://api.repo.nypl.org/api/v2/items/item_details/%s"

if __name__ == "__main__":
    for item in load_items("data/images.ndjson"):
        if item.id.endswith("f"):
            continue
        url = DETAILS_URL % item.uuid
        print(f"{url}\t{item.id}.json")
