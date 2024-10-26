#!/usr/bin/env python
"""Which is better, on-site OCR or GPT?"""

import base64
import csv
import json
import random
import sys
from collections import Counter, defaultdict

from tqdm import tqdm

from oldnyc.feedback.feedback_types import FeedbackJson
from oldnyc.item import load_items
from oldnyc.ocr.cleaner import clean
from oldnyc.ocr.score_utils import score_for_pair
from oldnyc.site.dates_from_text import get_dates_from_text
from oldnyc.site.site_data_type import SiteJson

MAGIC_COOKIES = dict(
    [
        ("c7e2f9fd-badf-4cfc-b0f5-ae5861629643", 909),
        ("42fedf3e-fa45-417f-89b0-d9706e6b8806", 566),
        ("9433591f-cbb0-458d-b989-f75ce30337ee", 453),
        ("9d75c4af-5ef0-4c21-aebc-162dd428fcea", 277),
        ("fe65fd56-1668-4d78-8695-84004c6e1b52", 245),
        ("c12d1c0a-6383-4f4a-abeb-bc2b60886fc7", 245),
        ("ae4598dd-17b1-48ae-89df-bc650759a304", 181),
        ("2080d5a6-d990-47e3-9c60-146fff0fb030", 174),
        ("3d5146c9-f261-4909-9292-94c755a4de61", 156),
        ("8c8ea4b3-3d11-4706-b409-2cdc2de9f613", 142),
        ("b79ea804-fd6d-48a4-b713-8b1a661bbaf0", 100),
        ("a911757f-4600-4652-a936-f5fa5802172e", 95),
    ]
)

REVIEW_IDS = [
    "702721b",
    "710751b",
    "722429b",
    "708430b",
    "713540b",
    "720613b",
    "708219b",
    "706197b",
    "716964b",
    "721093b",
    "713032b",
    "713837b",
    "720759b",
    "732005b",
    "715303b",
    "709384b",
    "714984b",
    "714924b",
    "723768b",
    "722191b",
    "709696b",
    "730801b",
    "731066b",
    "708980b",
    "722203b",
    "709493b",
    "708270b",
    "715230b",
    "720533b",
    "715250b",
    "725253b",
    "731918b",
    "721271b",
    "706651b",
    "710771b",
    "726175b",
    "719979b",
    "710972b",
    "723848b",
    "707959b",
    "715399b",
    "706851b",
    "712015b",
    "710729b",
    "721658b",
    "717646b",
    "724446b",
    "710977b",
    "721560b",
    "707700b",
    "708126b",
    "712398b",
    "715999b",
    "727606b",
    "710286b",
    "731942b",
    "725266b",
    "711476b",
    "715026b",
    "721196b",
    "713055b",
    "712754b",
    "711488b",
    "731936b",
    "724444b",
    "718056b",
    "730805b",
    "722349b",
    "722470b",
    "722117b",
    "708429b",
    "710692b",
    "708261b",
    "716619b",
    "714250b",
    "723954b",
    "710750b",
    "715207b",
    "714167b",
    "713704b",
    "706253b",
    "708220b",
    "717649b",
    "725652b",
    "724218b",
    "706186b",
    "718948b",
    "723200b",
    "708244b",
    "711860b",
    "722251b",
    "718906b",
    "733419b",
    "709959b",
    "717664b",
    "720364b",
    "724483b",
    "708007b",
    "716001b",
    "708209b",
]


def main():
    photos = load_items("data/photos.ndjson")
    back_to_photo_id = {r.back_id: r.id for r in photos if r.back_id}

    site_text: dict[str, str] = json.load(open("data/site-ocr-2024.json"))

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

    feedback_json: FeedbackJson = json.load(open("data/feedback/user-feedback.json"))
    magically_touched = set[str]()
    for back_id, v in feedback_json["feedback"].items():
        if "text" not in v:
            continue
        for c in v["text"].values():
            m = c["metadata"]
            cookie = m.get("cookie")
            if cookie in MAGIC_COOKIES:
                magically_touched.add(back_id)

    sys.stderr.write(f"{len(magically_touched)=}\n")

    # Keep an ID from the existing site if:
    # 1. It's marked as such in a manual review of big changes
    # 2. It's a big edit from a magic cookie
    # 3. It has more unique dates than the GPT version.
    keep_ids = defaultdict[str, list[str]](list)
    with open("/Users/danvk/Documents/oldnyc/big-changes.txt") as f:
        for row in csv.DictReader(f):
            back_id = row["back_id"]
            if row["Before"] or row["Before (minor)"]:
                keep_ids[back_id].append("big_change_manual")

    random.shuffle(both_ids)
    n_match = 0
    n_date_mismatch = 0
    n_uniq_date_mismatch = 0
    changes = []
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
            if len(set(dates_gpt)) < len(set(dates_site)):
                n_uniq_date_mismatch += 1
                keep_ids[id].append("uniq_dates")

        score, d, adjusted = score_for_pair(site, gpt)
        distances[d] += 1
        if score == 1.0:
            n_match += 1
        if d >= 10 and id in magically_touched:
            keep_ids[id].append("big_magic_cookie")
        elif d >= 70:  #  and id in magically_touched:  # and is_mismatch:
            # if id in REVIEW_IDS:
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
            # print(id, "\t", d)
        else:
            # break
            pass

        # if d > 500:
        #     print(f"{id} {d=} {len(site)=} {len(gpt)=}")

    changes.sort(key=lambda x: x["metadata"]["distance"], reverse=True)
    task_out = csv.DictWriter(open("data/feedback/review/changes.txt", "w"), ["back_id", "BASE64"])
    task_out.writeheader()
    task_out.writerows(
        {
            "back_id": change["photo_id"],
            "BASE64": base64.b64encode(json.dumps(change).encode("utf8")).decode("utf-8"),
        }
        for change in changes
    )

    open("data/feedback/review/changes.js", "w").write(
        "var changes = %s;" % json.dumps(changes, indent=2, sort_keys=True)
    )
    open("data/site-ocr-keep-ids.txt", "w").write(json.dumps(keep_ids, indent=2, sort_keys=True))

    sys.stderr.write(f"{n_match=}\n")
    sys.stderr.write(f"{n_date_mismatch=}\n")
    sys.stderr.write(f"{n_uniq_date_mismatch=}\n")
    sys.stderr.write(f"Num keeping from site: {len(keep_ids)}\n")
    # for d in sorted(distances.keys()):
    #     sys.stderr.write(f"{d}\t{distances[d]}\n")


if __name__ == "__main__":
    main()
