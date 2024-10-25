#!/usr/bin/env python
"""Split single images in images.ndjson into multiple records in photos.ndjson."""

import copy
import dataclasses
import json
import os
import sys
from dataclasses import dataclass

from tqdm import tqdm

from oldnyc.crop.extract_photos import ExtractedPhoto
from oldnyc.item import load_items


@dataclass
class Size:
    width: int
    height: int


@dataclass
class Crop(Size):
    top: int
    left: int


@dataclass
class Photo:
    crops: dict[str, Crop]
    metadata: Size


def load_crops(crops_ndjson: str) -> dict[str, Photo]:
    """Index crops.ndjson by input image file."""
    out: dict[str, Photo] = {}
    with open(crops_ndjson) as f:
        for line in f:
            d: ExtractedPhoto = json.loads(line)
            crops: dict[str, Crop] = {}
            if "rects" in d:
                for r in d["rects"]:
                    crops[os.path.basename(r["file"])] = Crop(
                        top=r["top"],
                        left=r["left"],
                        width=r["right"] - r["left"],
                        height=r["bottom"] - r["top"],
                    )
            out[os.path.basename(d["file"])] = Photo(
                crops=crops,
                metadata=Size(width=d["shape"]["w"], height=d["shape"]["h"]),
            )
    return out


if __name__ == "__main__":
    assert len(sys.argv) == 4, "Usage: %s imges.ndjson crops.ndjson photos.ndjson"
    _, records_ndjson, crops_ndjson, out_ndjson = sys.argv

    rs = load_items(records_ndjson)
    expansions = load_crops(crops_ndjson)

    skipped = 0
    num_images, num_photos = 0, 0

    out = []
    for idx, r in enumerate(tqdm(rs)):
        digital_id = r.id
        image_file = "%s.jpg" % digital_id
        expansion = expansions.get(image_file) or Photo(crops={}, metadata=Size(0, 0))

        num_images += 1

        crops = expansion.crops
        if len(crops) == 0:
            # r.thumbnail_url = image_file
            r.photo_url = image_file
            out.append(r)
            num_photos += 1
        else:
            for photo_file in crops.keys():
                new_r = copy.deepcopy(r)
                new_id, _ = os.path.splitext(photo_file)
                new_r.id = new_id
                new_r.photo_url = photo_file
                out.append(new_r)
                num_photos += 1

    sys.stderr.write("Skipped %d records\n" % skipped)
    with open(out_ndjson, "w") as f:
        for r in out:
            f.write(json.dumps(dataclasses.asdict(r)))
            f.write("\n")
    sys.stderr.write("Wrote %d records\n" % len(out))
