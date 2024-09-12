#!/usr/bin/env python
"""Gather output from a nougat-out directory into a JSON file for evaluation."""

import json
import os
import sys
from pathlib import Path

from ocr.cleaner import clean


if __name__ == '__main__':
    nougat_dir = sys.argv[1]
    mapping = {}
    for p in Path(nougat_dir).glob('*.mmd'):
        (back_id, _ext) = os.path.splitext(p.name)
        with open(p) as f:
            text = f.read()
        mapping[back_id] = clean(text)

    print(json.dumps(mapping, indent=2))
