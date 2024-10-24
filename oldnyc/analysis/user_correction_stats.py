#!/usr/bin/env python
"""What fraction of images have user corrections, and how many?"""

import json
import sys
from collections import Counter

from oldnyc.feedback.feedback_types import FeedbackJson

if __name__ == "__main__":
    originals = {
        k.replace("book", ""): v for k, v in json.load(open("data/ocr-ocropus-2015.json")).items()
    }
    feedback_json: FeedbackJson = json.load(open("data/feedback/user-feedback.json"))
    feedback = feedback_json["feedback"]
    counts = {back_id: len(v["text"]) for back_id, v in feedback.items() if "text" in v}

    # print(json.dumps(counts, indent=2, sort_keys=True))

    n = 0
    for back_id, count in counts.items():
        if count > 1:
            n += 1

    cookie_counts = Counter[str]()
    for back_id, v in feedback.items():
        if "text" in v:
            for c in v["text"].values():
                m = c["metadata"]
                cookie = m.get("cookie")
                # ip = m.get("user_ip") or "unknown"
                if cookie:
                    cookie_counts[cookie] += 1

    sys.stderr.write(f"unique cookies: {len(cookie_counts)}\n")
    num_total = sum(cookie_counts.values())
    for count in (100, 50, 25, 10):
        biggies = {c: v for c, v in cookie_counts.items() if v >= count}
        num_biggies = sum(biggies.values())
        sys.stderr.write(f"  {count}: {len(biggies)} => {num_biggies} / {num_total}\n")

    print(cookie_counts.most_common(12))
    print(cookie_counts["54a2c38e-2dee-433f-90b9-db0741e571c1"])

    # for (cookie, ip), count in cookie_counts.items():
    #     if cookie == "54a2c38e-2dee-433f-90b9-db0741e571c1":
    #         sys.stderr.write(f"{cookie} / {ip}: {count}\n")

    sys.stderr.write(f"{len(originals)} images have Ocropus OCR\n")
    sys.stderr.write(f"{len(counts)} images have corrections\n")
    sys.stderr.write(f"{n} images have multiple corrections\n")
    n_zero = len(originals) - len(counts)
    sys.stderr.write(f"{n_zero} images have no corrections\n")
