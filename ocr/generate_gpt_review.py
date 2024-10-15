#!/usr/bin/env python
"""Generate changes.js to review golden vs. GPT OCR."""

import json
import sys

from data.item import load_items

if __name__ == "__main__":
    gpt_jsonl = sys.argv[1]
    gpt_data = [json.loads(line) for line in open(gpt_jsonl)]
    site_data = json.load(open("../oldnyc.github.io/data.json"))
    id_to_site_data = {r["photo_id"].split("-")[0]: r for r in site_data["photos"]}
    records = load_items("data/items.ndjson")
    id_to_records = {r.id: r for r in records}

    changes = []
    for r in gpt_data:
        photo_id = r["custom_id"]
        response = r["response"]
        assert response["status_code"] == 200
        choices = response["body"]["choices"]
        assert len(choices) == 1
        data_str = choices[0]["message"]["content"]
        try:
            data = json.loads(data_str)
        except Exception:
            sys.stderr.write(f"Bad JSON from GPT on: {photo_id}\n")
            data_str += '"}'
            data = json.loads(data_str)
        gpt_text = data["text"]

        site_text = id_to_site_data[photo_id]["text"]
        record = id_to_records[photo_id]
        changes.append(
            {
                "before": site_text,
                "after": gpt_text,
                "metadata": {
                    "cookie": "blah",
                    "title": record.title,
                    "alt_title": record.alt_title,
                },
                "photo_id": photo_id,
            }
        )

    with open("ocr/feedback/review/changes.js", "w") as out:
        out.write("var changes = %s;" % json.dumps(changes, indent=2, sort_keys=True))
