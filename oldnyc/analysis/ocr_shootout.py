#!/usr/bin/env python
"""Which is better, on-site OCR or GPT?"""

import base64
import csv
import json
import random
import re
import sys
from collections import Counter, defaultdict

from tqdm import tqdm

from oldnyc.feedback.feedback_types import FeedbackJson
from oldnyc.item import Item, load_items
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


OLD_NYC_WORDS = {
    "Bldg",
    "Co",  # Edison Co.
    "Sperr",  # P. L. Sperr
    "Armbruster",  # Eugene L. Armbruster Collection
    "Jenks",  # Gift of E. M. Jenks
    "Schwartz",  # Nathan M. Schwartz; "schwarz" is a word in the dictionary
    "astor",
    "lenox",
    "tilden",  # Astor, Lenox and Tilden foundation
    "neg",
    "nos",
    # this is pervasive
    "manhatten",
    "jan",
    "feb",
    "mar",
    "apr",
    "may",
    "jun",
    "jul",
    "aug",
    "sep",
    "sept",
    "oct",
    "nov",
    "dec",
    "Triboro",
}


def split_words(txt: str) -> list[str]:
    return re.findall(r"[a-zA-zé0-9]+", txt)


def get_suspect_words(text: str, words: set[str], extra_words: set[str]) -> list[str]:
    return [
        w
        for w in split_words(text)
        if w.lower() not in words
        and w not in words
        and not re.match(r"^\d+$", w)
        and w.lower() not in extra_words
    ]


def diff_lists(a: list, b: list) -> list:
    """Retursn items in a that are not in b, accounting for duplicates."""
    b = list(b)
    out = []
    for x in a:
        if x in b:
            b.remove(x)
        else:
            out.append(x)
    return out


def get_item_words(item: Item) -> set[str]:
    out = set[str]()
    out.update(split_words(item.title))
    for alt_title in item.alt_title:
        out.update(split_words(alt_title))
    if item.creator:
        out.update(split_words(item.creator))
    if item.source:
        out.update(split_words(item.source))
    s = item.subject
    for src in [s.name, s.temporal, s.geographic, s.topic]:
        out.update(w for x in src for w in split_words(x))

    return {w.lower() for w in out}


def load_streets(src_file: str) -> set[str]:
    out = set[str]()
    with open(src_file) as f:
        for row in f:
            street = row.strip()
            for word in split_words(street):
                if len(word) > 2 and not re.match(r"^\d", word):
                    out.add(word)
    return out


def main():
    photos = load_items("data/photos.ndjson")
    back_to_photo_id = {r.back_id: r.id for r in photos if r.back_id}
    back_to_photo = {r.back_id: r for r in photos if r.back_id}

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

    words = set(open("data/web2a.txt").read().split("\n"))
    words.update(open("data/enable2k.txt").read().split("\n"))  # includes plurals
    words.update(OLD_NYC_WORDS)
    # TODO: "ing" should not be a word

    manhattan_street_words = load_streets("data/originals/manhattan-streets.txt")
    brooklyn_street_words = load_streets("data/originals/brooklyn-streets.txt")
    print(f"{len(manhattan_street_words)=}, {len(brooklyn_street_words)=}")
    # print(sorted([*manhattan_street_words]))
    # print(sorted([*brooklyn_street_words]))
    words.update(manhattan_street_words)
    words.update(brooklyn_street_words)

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
    with open("data/originals/ocr-heavy-editor.ids.txt", "w") as out:
        for id in magically_touched:
            out.write(f"{id}\n")

    sys.stderr.write(f"{len(magically_touched)=}\n")

    # Keep an ID from the existing site if:
    # 1. It's marked as such in a manual review of big changes
    # 2. It's a big edit from a magic cookie
    # 3. It has more unique dates than the GPT version.
    manual = dict[str, str]()
    keep_ids = defaultdict[str, list[str]](list)
    with open("data/originals/ocr-big-movers.txt") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            back_id = row["back_id"]
            if row["Choice"] == "site":
                keep_ids[back_id].append("big_change_manual")
            manual[back_id] = row["Choice"]

    with open("data/originals/ocr-spelld25.txt") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            back_id = row["back_id"]
            if row["Choice"] == "site":
                keep_ids[back_id].append("spell_d25_manual")
            manual[back_id] = row["Choice"]

    random.shuffle(both_ids)
    n_match = 0
    n_date_mismatch = 0
    n_uniq_date_mismatch = 0
    n_corrected = 0
    n_fs_lincoln = 0
    n_fs_corrected = 0
    n_big_corrected = 0
    n_date_corrected = 0
    n_astor_lenox = 0
    changes = []
    distances = Counter[int]()
    for id in tqdm(both_ids):
        site = clean(site_text[id])
        gpt = clean(gpt_text[id])

        if id in manual:
            continue  # it's already been filed in keep_ids if needed

        dates_site = get_dates_from_text(site)
        dates_gpt = get_dates_from_text(gpt)
        is_mismatch = len(dates_gpt) < len(dates_site)
        # sys.stderr.write(f"{id} {dates_site=} {dates_gpt=}\n")
        # is_mismatch = True
        is_uniq_mismatch = False
        if is_mismatch:
            n_date_mismatch += 1
            if len(set(dates_gpt)) < len(set(dates_site)):
                n_uniq_date_mismatch += 1
                is_uniq_mismatch = True
                keep_ids[id].append("uniq_dates")

        score, d, adjusted = score_for_pair(site, gpt)
        distances[d] += 1
        if score == 1.0:
            n_match += 1

        if "f. s. lincoln" in gpt.lower():
            n_fs_lincoln += 1
        if "astor, lenox" in gpt.lower():
            n_astor_lenox += 1

        item_words = get_item_words(back_to_photo[id])
        n_before = get_suspect_words(site, words, item_words)
        n_after = get_suspect_words(gpt, words, item_words)

        is_magically_touched = d >= 10 and id in magically_touched
        if is_magically_touched:
            keep_ids[id].append("big_magic_cookie")
        if len(n_before) > len(n_after):
            n_corrected += 1
        if len(n_before) < len(n_after):  #  and id in magically_touched:  # and is_mismatch:
            keep_ids[id].append("spelling")
            # if id in REVIEW_IDS:
        elif len(n_after) < len(n_before):
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
                    "n_before": len(n_before),
                    "n_after": len(n_after),
                    "before": diff_lists(n_before, n_after),
                    "after": diff_lists(n_after, n_before),
                    "title": back_to_photo[id].title,
                },
            }
            changes.append(out)
            # if d >= 70:
            #     n_big_corrected += 1
            # elif is_uniq_mismatch:
            #     n_date_corrected += 1
            # elif is_magically_touched:
            #     pass
            # elif len(gpt) - len(site) > 25:
            #     changes.append(out)
            # else:
            # pass
            #     changes.append(out)
            # print(id, "\t", d)

        # if d > 500:
        #     print(f"{id} {d=} {len(site)=} {len(gpt)=}")

    # changes.sort(key=lambda x: x["metadata"]["distance"], reverse=True)
    sys.stderr.write(f"Items with more misspellings: {len(changes)}\n")
    sys.stderr.write(f"Items with fewer misspelling: {n_corrected}\n")
    changes = changes[:100]
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
    open("data/site-ocr-keep-ids.txt", "w").write(json.dumps(keep_ids, indent=2, sort_keys=True))

    sys.stderr.write(f"{n_match=}\n")
    sys.stderr.write(f"{n_date_mismatch=}\n")
    sys.stderr.write(f"{n_uniq_date_mismatch=}\n")
    sys.stderr.write(f"{n_fs_lincoln=}\n")
    sys.stderr.write(f"{n_astor_lenox=}\n")
    sys.stderr.write(f"{n_fs_corrected=}\n")
    sys.stderr.write(f"{n_big_corrected=}\n")
    sys.stderr.write(f"{n_date_corrected=}\n")
    sys.stderr.write(f"Num keeping from site: {len(keep_ids)}\n")
    # for d in sorted(distances.keys()):
    #     sys.stderr.write(f"{d}\t{distances[d]}\n")


if __name__ == "__main__":
    main()
