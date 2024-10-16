#!/usr/bin/env python

import json
import sys

(cookie,) = sys.argv[1:]
corrections = json.load(open("corrections.json"))

for photo_id, data in corrections.items():
    for correction in data["corrections"]:
        if correction["cookie"] == cookie:
            print(correction["datetime"], photo_id)
