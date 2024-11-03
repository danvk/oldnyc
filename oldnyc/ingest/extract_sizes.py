#!/usr/bin/env python
"""Determine the sizes of a bunch of images.

Usage:
./oldnyc/ingest/extract_sizes.py '*.jpg' > sizes.txt

Produces a CSV file with three columns:
file-basename-no-extension,width,height
"""

import argparse
import glob
import os.path

from PIL import Image


def image_size(path: str):
    image = Image.open(path)
    width, height = image.size
    return (width, height)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract image sizes")
    parser.add_argument("--file", action="store_true", help="Read image paths from a file")
    parser.add_argument("patterns", nargs="+", help="Patterns to match")
    args = parser.parse_args()

    for pattern in args.patterns:
        path_src = (
            (path.strip() for path in open(pattern).readlines())
            if args.file
            else glob.glob(pattern)
        )
        for path in path_src:
            width, height = image_size(path)
            base, _ = os.path.splitext(os.path.basename(path))
            print("%s,%d,%d" % (base, width, height))
