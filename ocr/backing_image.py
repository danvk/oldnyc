#!/usr/bin/env python

import json
import re

import record


def strip_photo_suffix(photo_id: str) -> str:
    return re.sub(r"-[a-z]*", "", photo_id)


if __name__ == "__main__":
    rs: list[record.Record] = json.load(open("nyc/records.json"))
    # all_photo_ids = {r["id"] for r in rs}

    # site_data = json.load(open("../oldnyc.github.io/data.json"))
    # photo_ids = [photo["photo_id"] for photo in site_data["photos"]]
    # photo_ids_with_text = {
    #     strip_photo_suffix(photo['photo_id'])
    #     for photo in site_data['photos']
    #     if photo['text']
    # }

    # photo_ids = all_photo_ids.difference(photo_ids_with_text)
    # photo_ids = photo_ids_with_text

    for r in rs:
        back_id = r["back_id"]
        if back_id:
            url = f"http://images.nypl.org/?id={back_id}&t=w"
            print("%s\t%s.jpg" % (url, back_id))
