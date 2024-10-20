#!/usr/bin/env python
"""
Given the output of find_pictures.py, extract the individual photos.
Outputs a JSON structure containing information about what was done.
"""

import fileinput
import json
import os
import subprocess
import sys
from typing import NotRequired, TypedDict

from oldnyc.crop.find_pictures import PhotoCrops, Rect, SizeWH

usage = "%s (detected-photos.txt|http://...) output-directory\n" % sys.argv[0]


class RectWithFile(Rect):
    file: str


class ExtractedPhoto(TypedDict):
    file: str
    shape: SizeWH
    rects: NotRequired[list[RectWithFile]]


def ExtractPhotos(d: PhotoCrops, output_dir: str) -> ExtractedPhoto:
    rects = d["rects"] if "rects" in d else None
    if not rects:
        # The algorithm took a pass on this image.
        # symlink the original image into the output directory.
        output_path = os.path.join(output_dir, os.path.basename(d["file"]))
        if not os.path.exists(output_path) or not os.path.samefile(d["file"], output_path):
            subprocess.check_output(["ln", "-sf", d["file"], output_path])
        return ExtractedPhoto(file=d["file"], shape=d["shape"])
    else:
        base, ext = os.path.splitext(os.path.basename(d["file"]))
        out_rects: list[RectWithFile] = []
        for idx, rect in enumerate(rects):
            char = chr(ord("a") + idx)
            output_path = os.path.join(output_dir, "%s-%s%s" % (base, char, ext))
            w = rect["right"] - rect["left"]
            h = rect["bottom"] - rect["top"]
            subprocess.check_output(
                [
                    "convert",
                    d["file"],
                    "-crop",
                    "%dx%d+%d+%d" % (w, h, rect["left"], rect["top"]),
                    output_path,
                ]
            )
            out_rects.append({**rect, "file": os.path.basename(output_path)})
        return ExtractedPhoto(file=d["file"], shape=d["shape"], rects=out_rects)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stderr.write(usage)
        sys.exit(1)

    output_dir = sys.argv.pop()

    for line in fileinput.input():
        d = json.loads(line)
        f = str(d["file"])

        crops = ExtractPhotos(d, output_dir)
        print(json.dumps(crops))
        sys.stdout.flush()
