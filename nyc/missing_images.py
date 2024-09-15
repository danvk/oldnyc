#!/usr/bin/env python
"""Find images that are on the site but not hosted on the NYPL bucket.

Prints out pairs suitable for crawling with ocr/url_fetcher.py.
"""

import csv
import json
import sys

if __name__ == "__main__":
    site_photos = json.load(open("../oldnyc.github.io/data.json"))["photos"]

    id_to_dims = {}
    for photo_id, width, height in csv.reader(open("nyc-image-sizes.txt")):
        id_to_dims[photo_id] = (int(width), int(height))

    for photo in site_photos:
        id = photo["photo_id"]
        if id in id_to_dims:
            continue
        if "-" in id:
            sys.stderr.write(f"Cropped image crawl will fail: {id}\n")
        print(f"images/{id}.jpg\thttps://images.nypl.org/?id={id}&t=w")
