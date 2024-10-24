#!/usr/bin/env python
"""Which is better, on-site OCR or GPT?"""

import base64
import csv
import json
import random
import sys
from collections import Counter

from tqdm import tqdm

from oldnyc.item import load_items
from oldnyc.ocr.cleaner import clean
from oldnyc.ocr.score_utils import score_for_pair
from oldnyc.site.dates_from_text import get_dates_from_text
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

    both_ids = [id for id in site_text if id in gpt_text]
    n_int = len(both_ids)
    sys.stderr.write(f"n_site={len(site_text)}\n")
    sys.stderr.write(f"n_gpt={len(gpt_text)}\n")
    sys.stderr.write(f"{n_int=}\n")

    random.shuffle(both_ids)
    n_match = 0
    n_out = 0
    n_date_mismatch = 0
    task_out = csv.DictWriter(open("data/feedback/review/changes.txt", "w"), ["back_id", "BASE64"])
    task_out.writeheader()
    distances = Counter[int]()
    for id in tqdm(both_ids):
        site = clean(site_text[id])
        gpt = clean(gpt_text[id])

        dates_site = get_dates_from_text(site)
        dates_gpt = get_dates_from_text(gpt)
        is_mismatch = len(dates_gpt) < len(dates_site)
        # sys.stderr.write(f"{id} {dates_site=} {dates_gpt=}\n")
        # is_mismatch = True
        if is_mismatch:
            n_date_mismatch += 1

        score, d, adjusted = score_for_pair(site, gpt)
        distances[d] += 1
        if score == 1.0:
            n_match += 1
        elif n_out < 100 and is_mismatch:
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
            task_out.writerow(
                {
                    "back_id": id,
                    "BASE64": base64.b64encode(json.dumps(out).encode("utf8")).decode("utf-8"),
                }
            )
            n_out += 1
        else:
            # break
            pass

        # if d > 500:
        #     print(f"{id} {d=} {len(site)=} {len(gpt)=}")

    sys.stderr.write(f"{n_match=}\n")
    sys.stderr.write(f"{n_date_mismatch=}\n")
    for d in sorted(distances.keys()):
        sys.stderr.write(f"{d}\t{distances[d]}\n")


if __name__ == "__main__":
    main()
