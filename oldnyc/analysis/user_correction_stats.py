#!/usr/bin/env python
"""What fraction of images have user corrections, and how many?"""

import json
import sys

if __name__ == "__main__":
    originals = {
        k.replace("book", ""): v for k, v in json.load(open("data/ocr-ocropus-2015.json")).items()
    }
    feedback = json.load(open("feedback/user-feedback.json"))["feedback"]
    counts = {back_id: len(v["text"]) for back_id, v in feedback.items() if "text" in v}

    print(json.dumps(counts, indent=2, sort_keys=True))

    n = 0
    for back_id, count in counts.items():
        if count > 1:
            n += 1

    sys.stderr.write(f"{len(originals)} images have Ocropus OCR\n")
    sys.stderr.write(f"{len(counts)} images have corrections\n")
    sys.stderr.write(f"{n} images have multiple corrections\n")
    n_zero = len(originals) - len(counts)
    sys.stderr.write(f"{n_zero} images have no corrections\n")
