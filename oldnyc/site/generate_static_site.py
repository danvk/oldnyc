#!/usr/bin/env python
"""Generate a static version of oldnyc.org consisting entirely of JSON."""

import argparse
import csv
import json
import re
import subprocess
import sys
import time
from collections import OrderedDict, defaultdict
from typing import Iterable, Sequence

from oldnyc.ingest.dates import extract_years
from oldnyc.item import load_items
from oldnyc.site import dates_from_text
from oldnyc.site.site_data_type import (
    DateFields,
    PopularPhoto,
    SiteItem,
    SiteJson,
    SitePhoto,
    SiteResponse,
    Timestamps,
)
from oldnyc.site.title_cleaner import is_pure_location

# Make sure the oldnyc.github.io repo is in a clean state.
git_status = subprocess.check_output("git -C ../oldnyc.github.io status --porcelain".split(" "))
if git_status.strip():
    sys.stderr.write("Make sure the ../oldnyc.github.io repo exists and is clean.\n")
    sys.exit(1)

parser = argparse.ArgumentParser(description="Generate oldnyc.org static site")
parser.add_argument(
    "--leave-timestamps-unchanged",
    action="store_true",
    help="Do not update timestamps. Makes a clean diff possible.",
)
args = parser.parse_args()

# TODO: replace this with JSON
# strip leading 'var popular_photos = ' and trailing ';'
popular_photos: list[PopularPhoto] = json.loads(open("data/popular-photos.js").read()[20:-2])
pop_ids = {x["id"] for x in popular_photos}

lat_lon_to_item_ids: dict[str, list[str]] = json.load(open("data/lat-lon-to-ids.json"))

rs = load_items("data/photos.ndjson")
id_to_record = {r.id: r for r in rs}
item_id_to_photo_ids = defaultdict[str, list[str]](list)
for r in rs:
    item_id = r.id.split("-")[0]
    item_id_to_photo_ids[item_id].append(r.id)

lat_lon_to_ids = {
    ll: [photo_id for item_id in item_ids for photo_id in item_id_to_photo_ids[item_id]]
    for ll, item_ids in lat_lon_to_item_ids.items()
}

id_to_dims: dict[str, tuple[int, int]] = {}
for photo_id, width, height in csv.reader(open("data/nyc-image-sizes.txt")):
    id_to_dims[photo_id] = (int(width), int(height))

self_hosted_ids = set[str]()
for photo_id, width, height in csv.reader(open("data/self-hosted-sizes.txt")):
    id_to_dims[photo_id] = (int(width), int(height))
    self_hosted_ids.add(photo_id)


# rotated images based on user feedback
user_rotations = json.load(open("data/rotations.json"))
id_to_rotation = user_rotations["fixes"]


# Load the previous iteration of OCR. Corrections are applied on top of this.
# old_data: SiteJson = json.load(open("../oldnyc.github.io/data.json"))
# old_photo_id_to_text = {r["photo_id"]: r["text"] for r in old_data["photos"] if r["text"]}
old_times: Timestamps = json.load(open("../oldnyc.github.io/timestamps.json"))
manual_ocr_fixes = json.load(open("data/feedback/fixes.json"))
back_id_to_correction = manual_ocr_fixes["fixes"]
print(f"{len(back_id_to_correction)} OCR fixes")

# manual_ocr_fixes = {
#     'last_date': '2017-06-04T15:09:35',
#     'last_timestamp': 1496603375454,
# }
id_to_text: dict[str, str] = {}
for photo_id, r in id_to_record.items():
    if r.back_text:
        id_to_text[photo_id] = r.back_text
    if r.back_id in back_id_to_correction:
        id_to_text[photo_id] = back_id_to_correction[r.back_id]["text"]


def image_url(photo_id: str, is_thumb: bool) -> str:
    if photo_id in self_hosted_ids:
        return "https://images.nypl.org/?id=%s&t=w" % photo_id
    degrees = id_to_rotation.get(photo_id)
    if not degrees:
        return "https://oldnyc-assets.nypl.org/%s/%s.jpg" % (
            "thumb" if is_thumb else "600px",
            photo_id,
        )
    else:
        return "https://www.oldnyc.org/rotated-assets/%s/%s.%s.jpg" % (
            "thumb" if is_thumb else "600px",
            photo_id,
            degrees,
        )


def make_response(photo_ids: Iterable[str]):
    response: list[SiteResponse] = []
    for photo_id in photo_ids:
        r = id_to_record[photo_id]
        dims = id_to_dims.get(photo_id)
        if not dims:
            sys.stderr.write(f"Missing dimensions for {photo_id}\n")
            dims = (600, 400)
        w, h = dims
        # The UI expects images to be thumbnailed to 600px.
        if w > h and w > 600:
            h = int(round(600 * h / w))
            w = 600
        elif h > w and h > 600:
            w = int(round(600 * w / h))
            h = 600
        ocr_text = id_to_text.get(photo_id)

        title = r.title
        original_title = None
        if is_pure_location(title):
            original_title = title
            title = ""

        rotation = id_to_rotation.get(photo_id)
        if rotation and (rotation % 180 == 90):
            w, h = h, w

        date = re.sub(r"\s+", " ", r.date) if r.date else ""
        if len(date) > 4 and re.match(r"^\d+$", date):
            # TODO: is this still relevant?
            # There are some implausible dates like "13905" for https://www.oldnyc.org/#701590f-a
            # Best to hide these or (better) extract them from the backing text.
            date = ""
        date = date.replace(", ", "; ")
        date_fields: DateFields = {
            "date_source": "nypl",
            "date": date,
            "years": extract_years(date),
        }
        if (not date or date == "n.d") and ocr_text:
            new_dates = dates_from_text.get_dates_from_text(ocr_text)
            if new_dates:
                years = [d[:4] for d in new_dates]
                date_fields = {
                    "date_source": "text",
                    "date": "; ".join(sorted(set(years))),
                    "dates_from_text": new_dates,
                    "years": years,
                }
        resp: SiteResponse = {
            "id": photo_id,
            "title": title,
            **date_fields,
            "width": w,
            "height": h,
            "text": ocr_text,
            "image_url": image_url(photo_id, is_thumb=False),
            "thumb_url": image_url(photo_id, is_thumb=True),
            "nypl_url": f"https://digitalcollections.nypl.org/items/{r.uuid}",
            # TODO: switch to r.url after reviewing other diffs
        }
        if original_title:
            resp["original_title"] = original_title
        if rotation:
            resp["rotation"] = rotation

        # sort the keys for more stable diffing
        # we can't just use sort_keys=True in json.dump because the photo_ids
        # in the response have a meaningful sort order.
        response.append({k: resp[k] for k in sorted(resp.keys())})  # type: ignore

    # Sort by earliest date; undated photos go to the back. Use id as tie-breaker.
    response.sort(key=lambda rec: (min(rec["years"]) or "z", rec["id"]))
    return response


def group_by_year(response: Sequence[SiteItem]) -> OrderedDict[str, int]:
    counts = defaultdict(int)
    for rec in response:
        for year in extract_years(rec["date"]):
            counts[year] += 1
    return OrderedDict((y, counts[y]) for y in sorted(counts.keys()))


def site_response_to_site_json(r: SiteResponse, latlon: tuple[float, float]) -> SitePhoto:
    copy = SiteItem(r)
    # TODO: use "id" instead of "photo_id" in data.json. Or find a better way to type this.
    del copy["id"]  # type: ignore
    lat, lon = latlon
    return SitePhoto(
        {
            **copy,
            "photo_id": r["id"],
            "location": {"lat": lat, "lon": lon},
        }
    )


SORT_PRETTY = {"indent": 2, "sort_keys": True}

all_photos: list[SitePhoto] = []
latlon_to_count: dict[str, dict[str, int]] = {}
id4_to_latlon = defaultdict[str, dict[str, str]](dict)  # first 4 of id -> id -> "lat,lon"
textless_photo_ids: list[str] = []
for latlon, photo_ids in lat_lon_to_ids.items():
    outfile = "../oldnyc.github.io/by-location/%s.json" % latlon.replace(",", "")
    photos = make_response(photo_ids)
    latlon_to_count[latlon] = group_by_year(photos)
    # indentation has minimal impact on size here.
    json.dump(photos, open(outfile, "w"), indent=2, sort_keys=True)
    for id_ in photo_ids:
        id4_to_latlon[id_[:4]][id_] = latlon

    lat, lon = [float(x) for x in latlon.split(",")]
    for response in photos:
        photo_id = response["id"]
        if not response["text"] and "f" in photo_id:
            textless_photo_ids.append(photo_id)
        all_photos.append(site_response_to_site_json(response, (lat, lon)))

photo_ids_on_site = {photo["photo_id"] for photo in all_photos}
item_ids_on_site = {id.split("-")[0] for id in photo_ids_on_site}

missing_popular = {id_ for id_ in pop_ids if id_ not in photo_ids_on_site}
sys.stderr.write(f"Missing popular: {sorted(missing_popular)}\n")
print("Date extraction stats:")
dates_from_text.log_stats()

timestamps: Timestamps = {
    "timestamp": (
        old_times["timestamp"]
        if args.leave_timestamps_unchanged
        else time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    ),
    "rotation_time": user_rotations["last_date"],
    "ocr_time": (
        old_times["ocr_time"] if args.leave_timestamps_unchanged else manual_ocr_fixes["last_date"]
    ),
    "ocr_ms": (
        old_times["ocr_ms"]
        if args.leave_timestamps_unchanged
        else manual_ocr_fixes["last_timestamp"]
    ),
}

# This file may be unused.
json.dump(make_response(pop_ids), open("../oldnyc.github.io/popular.json", "w"), **SORT_PRETTY)

timestamps_json = json.dumps(timestamps, **SORT_PRETTY)

# This is part of the initial page load for OldNYC. File size matters.
with open("../oldnyc.github.io/static/lat-lon-counts.js", "w") as f:
    lat_lons_json = json.dumps(latlon_to_count, sort_keys=True, separators=(",", ":"))
    f.write(
        f"""
        var lat_lons = {lat_lons_json};
        var timestamps = {timestamps_json};
    """.strip()
    )

# These files are all pretty small; pretty-printing and sorting isn't harmful.
for id4, id_to_latlon in id4_to_latlon.items():
    json.dump(
        id_to_latlon, open("../oldnyc.github.io/id4-to-location/%s.json" % id4, "w"), **SORT_PRETTY
    )

# List of photos IDs without backing text.
# This is only used in the OCR correction tool, so file size is irrelevant.
json.dump(
    {"photo_ids": [*sorted(textless_photo_ids)]},
    open("../oldnyc.github.io/static/notext.json", "w"),
    **SORT_PRETTY,
)

all_photos.sort(key=lambda photo: photo["photo_id"])

# Complete data dump -- file size does not matter.
site_json: SiteJson = {
    "photos": all_photos,
    **timestamps,
}
json.dump(
    site_json,
    open("../oldnyc.github.io/data.json", "w"),
    **SORT_PRETTY,
)

# TODO: Remove this one and delete from repo once it's unused.
json.dump(timestamps, open("../oldnyc.github.io/timestamps.json", "w"), **SORT_PRETTY)

with open("../oldnyc.github.io/static/timestamps.js", "w") as f:
    f.write(f"var timestamps = {timestamps_json};")

sys.stderr.write(f"NYPL items on site: {len(item_ids_on_site)}\n")
sys.stderr.write(f"Unique photos on site: {len(photo_ids_on_site)}\n")
sys.stderr.write(f"Text-less photos: {len(textless_photo_ids)}\n")
sys.stderr.write(f"Unique lat/lngs: {len(latlon_to_count)}\n")
sys.stderr.write(f"Orphaned popular photos: {len(missing_popular)} / {len(pop_ids)}\n")
