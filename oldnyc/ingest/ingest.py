#!/usr/bin/env python
"""Read in various data sources and produce images.ndjson."""

# pyright: strict
import csv
import dataclasses
import json
import re
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


def outside_nyc(geographics: list[str]) -> bool:
    for g in geographics:
        if g in STATES and g not in TRISTATE:
            return True
    return False


def run():
    csv2013 = csv.DictReader(open("data/originals/milstein.csv", encoding="latin-1"))
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
    for row in tqdm([*csv2013]):
        counters["num records"] += 1
        id = row["DIGITAL_ID"]

        date_str = row["CREATED_DATE"]

        full_address = row["Full Address"].strip()

        title = row["IMAGE_TITLE"].strip()
        assert title

        alt_title = row["ALTERNATE_TITLE"].strip()
        if not alt_title:
            alt_title = None
        source = row["SOURCE"].strip()

        creator = row["CREATOR"].strip()

        row2 = csv2024[id]
        uuid = row2["item_uuid"]
        url = row2["digital_collections_url"]
        title2 = row2["title"].strip()
        date2 = row2["date"]
        if date2 == "1887, 1986" or date2 == "1870, 1970":
            date2 = ""  # 1887-1986 is used as "unknown"
            counters["date2: generic"] += 1

        topics = sort_uniq(json.loads(row2["subject/topic"]))
        geographics = sort_uniq(json.loads(row2["subject/geographic"]))
        names = sort_uniq(json.loads(row2["subject/name"]))
        temporals = sort_uniq(json.loads(row2["subject/temporal"]))

        dates = [date_str, date2]
        dates = [clean_date(normalize_whitespace(d.strip())) for d in dates]
        date_str, date2 = dates
        if date_str != date2:
            counters["mismatch: date"] += 1
            if date2 and not date_str:
                counters["date: added"] += 1
            elif date_str and not date2:
                counters["date: dropped"] += 1
            else:
                counters["date: changed"] += 1

            # print("---")
            # print(id)
            # print(date_str)
            # print(date2)

        titles = [title, title2]
        titles = [clean_title(normalize_whitespace(t)) for t in titles]
        title, title2 = titles

        if title != title2:
            counters["mismatch: title mismatch"] += 1
            # print("---")
            # print(title)
            # print(title2)

        mods_detail = mods_details.get(uuid)
        # TODO: store as array
        alt_title2 = (
            "\n".join(mods_detail.get("titles"))
            if mods_detail
            else (row2["alternative_title"].strip() if row2["alternative_title"] else None)
        )
        alt_titles = [alt_title, alt_title2]
        alt_titles = [clean_title(normalize_whitespace(t)) if t else None for t in alt_titles]
        alt_title, alt_title2 = alt_titles

        if alt_title != alt_title2:
            counters["mismatch: alt_title mismatch"] += 1
            # print("---")
            # print(alt_title)
            # print(alt_title2)
        alt_title2 = mods_detail.get("titles")[1:] if mods_detail else None
        if not alt_title2:
            alt_title2 = [row2["alternative_title"].strip()] if row2["alternative_title"] else []

        if alt_title:
            counters["alt_title"] += 1
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
        if "Directories" in topics:
            counters["filtered: directory"] += 1
            continue

        r = Item(
            id=id,
            uuid=uuid,
            url=url,
            photo_url=f"https://images.nypl.org/?id={id}&t=w",
            date=date2 or date_str or None,
            title=title2,
            alt_title=alt_title2 or [],
            back_id=back_id,
            creator=clean_creator(creator) or None,
            source=source,
            address=full_address,
            back_text=back_text,
            back_text_source=back_text_source,
            subject=Subject(name=names, temporal=temporals, geographic=geographics, topic=topics),
        )
        out.write(json.dumps(dataclasses.asdict(r)))
        out.write("\n")
        counters["outputs"] += 1

    for k in sorted(counters.keys()):
        v = counters[k]
        print(f"{v}\t{k}")


if __name__ == "__main__":
    run()
