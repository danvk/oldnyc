#!/usr/bin/env python
"""Read in various data sources and produce images.ndjson."""

# pyright: strict
import csv
import dataclasses
import json
import re
import sys
from collections import Counter

from tqdm import tqdm

from oldnyc.ingest.util import STATES, clean_creator, clean_date, clean_title, normalize_whitespace
from oldnyc.item import Item, Subject
from oldnyc.ocr.cleaner import clean as clean_ocr


def photo_id_to_backing_id(photo_id: str) -> str | None:
    if "f" in photo_id:
        return re.sub(r"f?(?:-[a-z])?$", "b", photo_id, count=1)
    elif re.match(r"\d+$", photo_id):
        front = int(photo_id)
        back = front + 1
        return str(back)
    return None


def sort_uniq(xs: list[str]) -> list[str]:
    out: list[str] = []
    for x in sorted(xs):
        if not out or out[-1] != x:
            out.append(x)
    return out


TRISTATE = {"New York", "New Jersey", "Connecticut"}
OTHER_OUTSIDE = {
    "West (U.S.)",
    "Southwest, New",
    "Nome (Alaska)",
    "Cumberland (Md.)",
    "Harpers Ferry (W. Va.)",
}


def outside_nyc(geographics: list[str]) -> bool:
    for g in geographics:
        if (g in STATES and g not in TRISTATE) or g in OTHER_OUTSIDE:
            return True
    return False


def strip_punctuation(s: str) -> str:
    return re.sub(r"[^\w]", "", s)


def run():
    csv2024 = {
        row["image_id"].lower(): row
        for row in csv.DictReader(open("data/originals/Milstein_data_for_DV_2.csv"))
    }
    # back_id -> text as it was on the site in September 2024
    site_text: dict[str, str] = json.load(open("data/site-ocr-2024.json"))
    gpt_text: dict[str, str] = {
        id: r["text"]
        for id, r in json.load(open("data/gpt-ocr.json")).items()
        if r["text"] != "(rotated)"
    }
    site_ocr_back_ids_to_keep = set[str](json.load(open("data/site-ocr-keep-ids.txt")).keys())
    mods_details = json.load(open("data/mods-details.json"))

    counters = Counter[str]()
    out = open("data/images.ndjson", "w")
    for id, row2 in tqdm([*csv2024.items()]):
        counters["num records"] += 1

        uuid = row2["item_uuid"]
        url = row2["digital_collections_url"]
        title2 = row2["title"].strip()

        topics = sort_uniq(json.loads(row2["subject/topic"]))
        geographics = sort_uniq(json.loads(row2["subject/geographic"]))
        names = sort_uniq(json.loads(row2["subject/name"]))
        temporals = sort_uniq(json.loads(row2["subject/temporal"]))

        date2 = row2["date"]
        if date2 == "1887, 1986" or date2 == "1870, 1970":
            date2 = ""  # 1887-1986 is used as "unknown"
            counters["date2: generic"] += 1
        date2 = clean_date(normalize_whitespace(date2.strip()))

        title2 = clean_title(normalize_whitespace(title2))

        mods_detail = mods_details.get(uuid)
        alt_title2 = mods_detail.get("titles")[1:] if mods_detail else None
        if not alt_title2:
            alt_title2 = [row2["alternative_title"].strip()] if row2["alternative_title"] else []
        alt_title2 = [clean_title(normalize_whitespace(t)) for t in alt_title2]

        if alt_title2:
            counters["alt_title2"] += 1

        back_id = photo_id_to_backing_id(id) if id.endswith("f") else None
        if not back_id and mods_detail:
            back_id = mods_detail.get("back_id")

        ocr_site = site_text.get(back_id) if back_id else None
        if back_id not in site_text:
            counters["ocr: site: missing"] += 1
        elif ocr_site is None or ocr_site == "":
            counters["ocr: site: blank"] += 1
        else:
            counters["ocr: site: present"] += 1

        counters["back_id: " + ("present" if back_id else "missing")] += 1
        ocr_gpt = gpt_text.get(back_id) if back_id else None
        if ocr_gpt:
            counters["ocr: gpt: present"] += 1
        if ocr_gpt and ocr_site:
            counters["ocr: gpt+ocr"] += 1
        if ocr_gpt or ocr_site:
            counters["ocr: either"] += 1
        if back_id:
            counters["ocr: has back"] += 1

        back_text: str | None = None
        back_text_source: str | None = None
        if ocr_gpt:
            back_text = clean_ocr(ocr_gpt)
            back_text_source = "gpt"
        if ocr_site and (not ocr_gpt or back_id in site_ocr_back_ids_to_keep):
            back_text = clean_ocr(ocr_site)
            back_text_source = "site"

        if back_text:
            # This matches the text that's gone through the OCR correction tool.
            back_text = back_text.strip()
            if "\n" in back_text:
                back_text += "\n"

        counters[f"back_text_source: {back_text_source}"] += 1

        if outside_nyc(geographics):
            counters["filtered: outside nyc"] += 1
            continue
        if ("Directories" in topics) or ("directory" in title2.lower()):
            counters["filtered: directory"] += 1
            continue

        r = Item(
            id=id,
            uuid=uuid,
            url=url,
            photo_url=f"https://images.nypl.org/?id={id}&t=w",
            date=date2 or None,
            title=title2,
            alt_title=alt_title2 or [],
            back_id=back_id,
            creator=clean_creator(creator) or None,
            source=source,
            back_text=back_text,
            back_text_source=back_text_source,
            subject=Subject(name=names, temporal=temporals, geographic=geographics, topic=topics),
        )
        out.write(json.dumps(dataclasses.asdict(r)))
        out.write("\n")
        counters["outputs"] += 1

    for k in sorted(counters.keys()):
        v = counters[k]
        sys.stderr.write(f"{v}\t{k}\n")


if __name__ == "__main__":
    run()
