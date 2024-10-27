#!/usr/bin/env python
"""Which is better, on-site OCR or GPT?"""

import base64
import csv
import json
import random
import sys

from oldnyc.item import load_items
from oldnyc.ocr.cleaner import clean
from oldnyc.ocr.score_utils import score_for_pair
from oldnyc.site.site_data_type import SiteJson


def main():
    items = load_items("data/images.ndjson")
    front_to_back = {r.id: r.back_id for r in items if r.back_id}

    site_data: SiteJson = json.load(open("../oldnyc.github.io/data.json"))
    site_text: dict[str, str] = {}
    back_to_photo_id = dict[str, str]()
    sys.stderr.write(f'{len(site_data["photos"])} photos on site\n')
    photo_id_backs = list[tuple[str, str]]()
    for photo in site_data["photos"]:
        id = photo["photo_id"].split("-")[0]
        back_id = front_to_back.get(id)
        if back_id and photo["text"]:
            site_text[back_id] = photo["text"]
            back_to_photo_id[back_id] = photo["photo_id"]
            photo_id_backs.append((photo["photo_id"], back_id))

    old_site: dict[str, str] = json.load(open("data/site-ocr-2024.json"))
    site_sample = random.sample(
        [back_id for _, back_id in photo_id_backs if back_id in old_site], 200
    )

    changes = []
    random.shuffle(site_sample)
    for id in site_sample:
        site = old_site[id]
        gpt = clean(site_text[id])

        score, d, adjusted = score_for_pair(site, gpt)
        if d == 0:
            continue
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
        changes.append(out)

    changes = changes[:100]
    # changes.sort(key=lambda x: x["metadata"]["distance"], reverse=True)
    task_out = csv.DictWriter(
        open("data/feedback/review/changes.txt", "w"), ["back_id", "distance", "BASE64"]
    )
    task_out.writeheader()
    task_out.writerows(
        {
            "back_id": change["photo_id"],
            "distance": change["metadata"]["distance"],
            "BASE64": base64.b64encode(json.dumps(change).encode("utf8")).decode("utf-8"),
        }
        for change in changes
    )

    open("data/feedback/review/changes.js", "w").write(
        "var changes = %s;" % json.dumps(changes, indent=2, sort_keys=True)
    )


if __name__ == "__main__":
    main()
