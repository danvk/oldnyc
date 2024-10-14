#!/usr/bin/env python
"""Evaluate the differences between two OCR files and output JS for manual review.

Input is two JSON files mapping back ID -> text (base and experiment).
Outputs some stats and fills in ocr/feedback/review/changes.js
"""

#

import json
import sys

from ocr.score_utils import score_for_pair
from record import Record


if __name__ == "__main__":
    (base_file, exp_file) = sys.argv[1:]

    base: dict[str, str] = json.load(open(base_file))
    exp: dict[str, str | dict] = json.load(open(exp_file))

    records: list[Record] = json.load(open("nyc/records.json"))
    id_to_record = {r["id"]: r for r in records}
    front_to_back = {r["id"]: r["back_id"] for r in records if r["back_id"]}
    site_data = json.load(open("../oldnyc.github.io/data.json"))
    back_to_front = {}
    for r in site_data["photos"]:
        id = r["photo_id"]
        photo_id = id.split("-")[0]
        back_id = front_to_back.get(photo_id)
        if back_id:
            back_to_front[back_id] = id

    scores = []
    changes = []
    for id, exp_item in exp.items():
        base_text = base[id]
        if isinstance(base_text, dict):
            base_text = base_text["text"]
        if isinstance(exp_item, dict):
            exp_text = exp_item["text"]
            orig_text = exp_item["original"]
        else:
            exp_text = exp_item
            orig_text = None
        (score, distance, adjusted_base) = score_for_pair(base_text, exp_text, id)
        scores.append(score)
        changes.append(
            {
                "photo_id": back_to_front.get(
                    id, id.replace("b", "f-a")
                ),  # should be back ID
                "before": adjusted_base,
                "after": exp_text,
                "metadata": {
                    "cookie": "eval",
                    "len_base": len(base_text),
                    "len_exp": len(exp_text),
                    "distance": distance,
                    "score": score,
                    "back_id": id,
                    "record": (
                        id_to_record[back_to_front[id].split("-")[0]]
                        if id in back_to_front
                        else None
                    ),
                    "raw_text": orig_text,
                },
            }
        )

    changes.sort(key=lambda r: r["metadata"]["score"])
    for i, change in enumerate(changes):
        # id = change['photo_id']
        back_id = change["metadata"]["back_id"]
        score = change["metadata"]["score"]
        distance = change["metadata"]["distance"]
        len_base = change["metadata"]["len_base"]
        len_exp = change["metadata"]["len_exp"]
        print(
            "%3d %s\t%.3f\t%4d\t%d\t%d"
            % (i + 1, back_id, score, distance, len_base, len_exp)
        )

    mean = sum(scores) / len(scores)
    print("Average: %.3f" % mean)

    open("ocr/feedback/review/changes.js", "w").write(
        "var changes = %s;" % json.dumps(changes, indent=2)
    )
