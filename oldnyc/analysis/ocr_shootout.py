#!/usr/bin/env python
"""Which is better, on-site OCR or GPT?"""

import csv
import json
import random
import sys

from tqdm import tqdm

from oldnyc.item import load_items
from oldnyc.ocr.score_utils import score_for_pair
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

    gpt_text: dict[str, str] = {
        id: r["text"]
        for id, r in json.load(open("data/gpt-ocr.json")).items()
        if r["text"] != "(rotated)"
    }

    n_int = sum(1 for id in site_text if id in gpt_text)
    sys.stderr.write(f"n_site={len(site_text)}\n")
    sys.stderr.write(f"n_gpt={len(gpt_text)}\n")
    sys.stderr.write(f"{n_int=}\n")

    ids = [*site_text.keys()]
    random.shuffle(ids)
    changes = []
    n_match = 0
    for id in tqdm(ids):
        if id not in gpt_text:
            continue
        site = site_text[id]
        gpt = gpt_text[id]
        score, d, adjusted = score_for_pair(site, gpt)
        out = {
            "photo_id": back_to_photo_id[id],
            "before": site,
            "after": gpt,
            "metadata": {
                "cookie": "blah",
                "len_base": len(site),
                "len_exp": len(gpt),
                "back_id": id,
                "distance": d,
                "score": score,
            },
        }
        if len(changes) < 100:
            changes.append(out)
        if score == 1.0:
            n_match += 1

    sys.stderr.write(f"{n_match=}\n")

    open("data/feedback/review/changes.js", "w").write(
        "var changes = %s;" % json.dumps(changes, indent=2, sort_keys=True)
    )


if __name__ == "__main__":
    main()
