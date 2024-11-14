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


CREATOR_PATCHES = {
    "Welles, Burton F. (Burton Frederick), 1872-": "Welles & Co.--Publisher",
    "Sperr, Percy Loomis, 1890-1964": "Sperr, Percy Loomis",
    "Wurts Bros. (New York, N.Y.)": "Wurts Brothers",
    "Ewing Galloway (Agency)": "Galloway, Ewing",
    "Underhill, Irving, -1960": "Underhill, Irving,d. 1960",
    "Tiemann, Hermann Newell (1863-1957)": "Tiemann, Hermann Newell",
    "Fass, John S. (John Stroble), 1890-1973": "Fass, John S. (John Stroble),b. 1890",
    "Van der Weyde, William M. (William Manley), 1870-1928": "Van der Weyde, William M. (William Manley)",
    "Abbott, Berenice, 1898-1991": "Abbott, Berenice",
    "Fairchild Aerial Surveys, inc.": "Fairchild Aerial Surveys, Inc.",
    "Armbruster, Eugene L., 1865-1943": "Armbruster, Eugene L.",
}

SOURCE_PATCHES = {
    "Fifth Avenue, New York, from start to finish": "Fifth Avenue, New York, from start to finish.",
    "Itineraire pittoresque du fleuve Hudson et des parties laterales de l'Amerique du Nord, d'apres les dessins originaux pris sur les lieux. Atlas": "Itineraire pittoresque du fleuve Hudson et des parties laterales de l'Amerique du Nord, d'apres les dessins originaux pris sur les lieux. Atlas.",
    "Apartment houses of the metropolis": "Apartment houses of the metropolis.",
    "Amerique septentrionale : vues des chutes du Niagara": "Amerique septentrionale : vues des chutes du Niagara.",
    "Photographic views of New York City, 1870's-1970's. Supplement. / Manhattan": "Photographic views of New York City, 1870's-1970's, from the collections of the New York Public Library. Supplement.  / Manhattan",
    "Photographic views of New York City, 1870's-1970's. Supplement. / Brooklyn": "Photographic views of New York City, 1870's-1970's, from the collections of the New York Public Library. Supplement.  / Brooklyn",
    "Photographic views of New York City, 1870's-1970's. Supplement. / Queens": "Photographic views of New York City, 1870's-1970's, from the collections of the New York Public Library. Supplement.  / Queens",
    "Photographic views of New York City, 1870's-1970's. Supplement. / Bronx": "Photographic views of New York City, 1870's-1970's, from the collections of the New York Public Library. Supplement.  / Bronx",
    "Photographic views of New York City, 1870's-1970's. Supplement. / Topics": "Photographic views of New York City, 1870's-1970's, from the collections of the New York Public Library. Supplement.  / Topics",
    "Collection of photographs of New York City / Manhattan": "[Collection of photographs of New York City.] / [Wurts Brothers, photographer] / Manhattan",
    "Collection of photographs of New York City / Brooklyn": "[Collection of photographs of New York City.] / [Wurts Brothers, photographer] / Brooklyn",
    "Collection of photographs of New York City / Bronx": "[Collection of photographs of New York City.] / [Wurts Brothers, photographer] / Bronx",
    "Collection of photographs of New York City / Queens": "[Collection of photographs of New York City.] / [Wurts Brothers, photographer] / Queens",
    "Collection of photographs of New York City / Subjects": "[Collection of photographs of New York City.] / [Wurts Brothers, photographer] / Subjects",
    "Collection of photographs of New York City, 1931-1942": "[Collection of photographs of New York City, 1931-1942.]",
    "Photographic negatives of the New York City Tenement House Department": "Photographic negatives of the New York City Tenement House Department, 1902-1914",
    "A Pictorial description of Broadway": "A Pictorial description of Broadway / by the Mail & Express.",
    "The World's loose leaf album of apartment houses: containing views and ground plans of the principal high class apartment houses in New York City, together with a map showing the situation of these houses, transportation facilities, etc.": "The World's loose leaf album of apartment houses, containing views and ground plans of the principal high class apartment houses in New York City, together with a map showing the situation of these houses, transportation facilities, etc.",
    "[Collection of photographs of New York City, 1931-1942]": "[Collection of photographs of New York City, 1931-1942.]",
    "Photographs of Madison Square Garden": "[Photographs of Madison Square Garden. New York, 1925]",
    "Forty etchings, from sketches made with the camera lucida, in North America, in 1827 and 1828": "Forty etchings, from sketches made with the camera lucida, in North America, in 1827 and 1828.",
    "Photographic views of the construction of the New York City subway system, 1901-1905": "Photographic views of the construction of the New York City subway system, 1901-1905.",
    "Supplement to Apartment houses of the metropolis": "Supplement to Apartment houses of the metropolis.",
}


def outside_nyc(geographics: list[str]) -> bool:
    for g in geographics:
        if (g in STATES and g not in TRISTATE) or g in OTHER_OUTSIDE:
            return True
    return False


def strip_punctuation(s: str) -> str:
    return re.sub(r"[^\w]", "", s)


def patch_source(source: str) -> str:
    if source == "":
        return ""
    source = source.replace(", from the collections of the New York Public Library", "")
    if source.startswith("Collection of photographs taken by Daniel B. Austin"):
        source = "[" + source
        source = source.replace("1914", "1914]")
    return SOURCE_PATCHES.get(source, source)


# These are sometimes used as placeholders for unknown dates.
GENERIC_DATES = {"1887, 1986", "1870, 1970", "1887, 1964", "1900, 1999", "1960, 1990"}


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
    ids = [*sorted(csv2024.keys())]
    for id in tqdm(ids):
        counters["num records"] += 1
        row2 = csv2024[id]

        uuid = row2["item_uuid"]
        url = row2["digital_collections_url"]
        title2 = row2["title"].strip()

        topics = sort_uniq(json.loads(row2["subject/topic"]))
        geographics = sort_uniq(json.loads(row2["subject/geographic"]))
        names = sort_uniq(json.loads(row2["subject/name"]))
        temporals = sort_uniq(json.loads(row2["subject/temporal"]))
        mods_detail = mods_details.get(uuid)

        date2 = row2["date"] or (mods_detail["date"] if mods_detail else None) or ""
        if date2 in GENERIC_DATES:
            date2 = ""
            counters["date2: generic"] += 1
        date2 = clean_date(normalize_whitespace(date2.strip()))

        title2 = clean_title(normalize_whitespace(title2))

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

        creator = (clean_creator(mods_detail["creator"] or "") or None) if mods_detail else None
        creator = CREATOR_PATCHES.get(creator, creator) if creator else None

        source = " / ".join(mods_detail["sources"]) if mods_detail else ""
        source = patch_source(source)

        r = Item(
            id=id,
            uuid=uuid,
            url=url,
            photo_url=f"https://images.nypl.org/?id={id}&t=w",
            date=date2 or None,
            title=title2,
            alt_title=alt_title2 or [],
            back_id=back_id,
            creator=creator,
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
