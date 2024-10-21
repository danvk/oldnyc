#!/usr/bin/env python
"""Determine the rotation of a backing image.

Given a high resolution image that may be rotated and a low-resolution one that isn't,
determine which rotation would make the high-resolution image best line up with the
low resolution image.
"""

import os
import shutil
import sys

import imagehash
from PIL import Image, ImageChops

if __name__ == "__main__":
    (high_path, low_path, out_dir) = sys.argv[1:]
    failed_ocrbacks = {
        line.split(".")[0] for line in open("data/ocrbacks.txt") if "original" in line
    }

    for ext in ("", ".jpg", ".reconstructed.jpg", ".original.jpg"):
        if os.path.exists(high_path + ext):
            high_path = high_path + ext
            break

    if not os.path.exists(high_path):
        sys.stderr.write(f"No high-resolution image for {high_path}; skipping...\n")
        sys.exit(0)

    id = os.path.basename(high_path).split(".")[0]

    is_fail = id in failed_ocrbacks
    hashd = 0
    high_im = None
    if is_fail:
        high_im = Image.open(high_path).convert("L")
        low_im = Image.open(low_path).convert("L")
        low_aspect = low_im.width / low_im.height
        low_hash = imagehash.phash(low_im)

        # TODO: this is wildly inefficient
        candidates = []
        for rot in (0, 90, 180, 270):
            rot_im = high_im.rotate(rot, expand=True)
            # print(f'{rot} size: {rot_im.width} x {rot_im.height}')
            rot_aspect = rot_im.width / rot_im.height
            if abs(rot_aspect - low_aspect) > 0.1:
                # print(f'{rot}: tossing based on aspect ratios: {rot_aspect:.3f}, want {low_aspect:.3f}')
                continue

            shrunk_im = rot_im.resize(low_im.size, resample=Image.Resampling.NEAREST)
            # shrunk_hash = imagehash.average_hash(shrunk_im)
            # print(low_im.size)
            # print(shrunk_im.size)
            diff = ImageChops.difference(low_im, shrunk_im)
            # print(diff.getbbox())
            score = len(set(diff.getdata()))  # type: ignore
            shrunk_hash = imagehash.phash(shrunk_im)
            candidates.append((score, rot, low_hash - shrunk_hash, str(shrunk_hash)))
            # print(f'{rot}: {shrunk_hash - low_hash} = {shrunk_hash} - {low_hash}')

        candidates.sort()
        # print(f'{id} Candidates: {candidates}')
        # for score, rot, hashd, hash_str in candidates:
        #    print(f'  {rot} {score=} {hashd=} {hash_str==low_hash_str} {hash_str} {low_hash_str}')
        # print(f'Best is: {rot}')
        if candidates:
            rot = candidates[0][1]
            hashd = candidates[0][2]
        else:
            rot = 0
            hashd = 64
    else:
        rot = 0
        # print(f'Skipping {id} because it is not in failed_ocrbacks')

    if is_fail:
        print(f"{id}: {rot}°\tphash d={hashd}/64")

        if hashd >= 16:
            print(f"{id}: rejecting likely DC vs. ocrbacks mismatch")
            sys.exit(0)

    out_path = os.path.join(out_dir, os.path.basename(low_path))
    if rot == 0:
        shutil.copy(high_path, out_path)
    else:
        assert high_im  # for pyright
        rot_im = high_im.rotate(rot, expand=True)
        rot_im.save(out_path)
    # print(f'Wrote {out_path}')
