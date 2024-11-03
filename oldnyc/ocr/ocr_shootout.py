#!/usr/bin/env python
"""Compare GPT OCR to the existing OCR and decide which one to use for each item.

See https://github.com/danvk/oldnyc/pull/146
"""

import csv
import json
import random
import re
import sys
from collections import Counter, defaultdict
from typing import TypeVar

from tqdm import tqdm

from oldnyc.item import Item, load_items
from oldnyc.ocr.cleaner import clean
from oldnyc.ocr.score_utils import score_for_pair
from oldnyc.site.dates_from_text import get_dates_from_text
from oldnyc.util import encode_json_base64

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


# TODO: switch to diff_lists[T] after upgrading to Python 3.12
T = TypeVar("T")


def diff_lists(a: list[T], b: list[T]) -> list[T]:
    """Returns items in a that are not in b, accounting for duplicates."""
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
    # back_to_photo_id = {r.back_id: r.id for r in photos if r.back_id}
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
    words.update(manhattan_street_words)
    words.update(brooklyn_street_words)

    magically_touched = set(open("data/originals/ocr-heavy-editor.ids.txt").read().split("\n"))
    sys.stderr.write(f"{len(magically_touched)=}\n")

    # Keep an ID from the existing site if:
    # 1. It's marked as such in a manual review of big changes
    # 2. It's a big edit from a magic cookie
    # 3. It has more unique dates than the GPT version.
    manual = dict[str, str]()
    keep_ids = defaultdict[str, list[str]](list)
    manual_sources = [
        ("data/originals/ocr-big-movers.txt", "big_change_manual"),
        ("data/originals/ocr-spelld25.txt", "spell_d25_manual"),
        ("data/originals/ocr-followup.txt", "followup_manual"),
    ]
    for src_file, label in manual_sources:
        with open(src_file) as f:
            for row in csv.DictReader(f, delimiter="\t"):
                back_id = row["back_id"]
                if row["Choice"] == "site":
                    keep_ids[back_id].append(label)
                manual[back_id] = row["Choice"]

    random.shuffle(both_ids)
    n_match = 0
    n_date_mismatch = 0
    n_uniq_date_mismatch = 0
    n_fs_corrected = 0
    n_big_corrected = 0
    n_date_corrected = 0
    n_misspell_increase = 0
    n_misspell_decrease = 0
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
        if is_mismatch:
            n_date_mismatch += 1
            if len(set(dates_gpt)) < len(set(dates_site)):
                n_uniq_date_mismatch += 1
                keep_ids[id].append("uniq_dates")

        score, d, adjusted = score_for_pair(site, gpt)
        distances[d] += 1
        if score == 1.0:
            n_match += 1

        item_words = get_item_words(back_to_photo[id])
        n_before = get_suspect_words(site, words, item_words)
        n_after = get_suspect_words(gpt, words, item_words)

        if len(n_before) < len(n_after):
            n_misspell_increase += 1
        elif len(n_after) < len(n_before):
            n_misspell_decrease += 1

        is_magically_touched = d >= 10 and id in magically_touched
        if is_magically_touched:
            keep_ids[id].append("big_magic_cookie")
        if len(n_before) < len(n_after):  #  and id in magically_touched:  # and is_mismatch:
            keep_ids[id].append("spelling")
            # if id in REVIEW_IDS:
        else:
            pass

        # Use this to populate review.js and review.txt
        # out = {
        #     "photo_id": back_to_photo_id[id],
        #     "before": site,
        #     "after": gpt,
        #     "metadata": {
        #         "cookie": "blah",
        #         "len_base": len(site),
        #         "len_exp": len(gpt),
        #         "back_id": id,
        #         "distance": d,
        #         "score": score,
        #         "n_before": len(n_before),
        #         "n_after": len(n_after),
        #         "before": diff_lists(n_before, n_after),
        #         "after": diff_lists(n_after, n_before),
        #         "title": back_to_photo[id].title,
        #     },
        # }
        # changes.append(out)

    # changes.sort(key=lambda x: x["metadata"]["distance"], reverse=True)
    sys.stderr.write(f"Items with more misspellings: {n_misspell_increase}\n")
    sys.stderr.write(f"Items with fewer misspelling: {n_misspell_decrease}\n")
    changes = changes[:100]
    task_out = csv.DictWriter(
        open("data/feedback/review/changes.txt", "w"), ["back_id", "distance", "BASE64"]
    )
    task_out.writeheader()
    task_out.writerows(
        {
            "back_id": change["photo_id"],
            "distance": change["metadata"]["distance"],
            "BASE64": encode_json_base64(change),
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
    sys.stderr.write(f"{n_fs_corrected=}\n")
    sys.stderr.write(f"{n_big_corrected=}\n")
    sys.stderr.write(f"{n_date_corrected=}\n")
    sys.stderr.write(f"Num keeping from site: {len(keep_ids)}\n")
    # for d in sorted(distances.keys()):
    #     sys.stderr.write(f"{d}\t{distances[d]}\n")


if __name__ == "__main__":
    main()
