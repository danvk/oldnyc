#!/usr/bin/env python
"""Determine the rotation of a backing image.

Given a high resolution image that may be rotated and a low-resolution one that isn't,
determine which rotation would make the high-resolution image best line up with the
low resolution image.
"""

import os
import shutil
import sys

from PIL import Image, ImageChops


if __name__ == '__main__':
    (high_path, low_path, out_dir) = sys.argv[1:]
    high_im = Image.open(high_path).convert("L")
    low_im = Image.open(low_path).convert("L")
    low_aspect = low_im.width / low_im.height

    failed_ocrbacks = {
        line.split('.')[0] for line in open('ocr/ocrbacks.txt') if 'original' in line
    }

    (id, _) = os.path.splitext(os.path.basename(high_path))
    print(f'{id=}')

    if id in failed_ocrbacks:
        # TODO: this is wildly inefficient
        candidates = []
        for rot in (0, 90, 180, 270):
            rot_im = high_im.rotate(rot, expand=True)
            # print(f'{rot} size: {rot_im.width} x {rot_im.height}')
            rot_aspect = rot_im.width / rot_im.height
            if abs(rot_aspect - low_aspect) > 0.1:
                print(f'{rot}: tossing based on aspect ratios: {rot_aspect:.3f}, want {low_aspect:.3f}')
                continue

            shrunk_im = rot_im.resize(low_im.size, resample=Image.Resampling.NEAREST)
            # shrunk_hash = imagehash.average_hash(shrunk_im)
            # print(low_im.size)
            # print(shrunk_im.size)
            diff = ImageChops.difference(low_im, shrunk_im)
            # print(diff.getbbox())
            score = len(set(diff.getdata()))
            candidates.append((score, rot))
            # print(f'{rot}: {shrunk_hash - low_hash} = {shrunk_hash} - {low_hash}')

        candidates.sort()
        print(f'Candidates: {candidates}')
        rot = candidates[0][1]
        print(f'Best is: {rot}')
    else:
        rot = 0
        print(f'Skipping {id} because it is not in failed_ocrbacks')

    out_path = os.path.join(out_dir, os.path.basename(high_path))
    if rot == 0:
        shutil.copy(high_path, out_path)
    else:
        rot_im = high_im.rotate(rot, expand=True)
        rot_im.save(out_path)
    print(f'Wrote {out_path}')
