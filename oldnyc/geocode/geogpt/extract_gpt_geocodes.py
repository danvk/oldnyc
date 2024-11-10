#!/usr/bin/env python
"""Extract photo ID -> geocodable string mapping from GPT JSONL output files."""

import json
import re
import sys
from collections import Counter

from oldnyc.geocode.geogpt.generate_batch import GptResponse


def patch_query(q: str) -> str:
    """GPT makes some systematic mistakes, for example combining addresses and crosses.

    This fixes that.
        4514 16th Avenue & 46th Street -> 16th Avenue & 46th Street
        131-135 Pitt St & E Houston St -> Pitt St & E Houston St
        334-336 Atlantic Avenue -> 336 Atlantic Avenue
    """
    q = re.sub(r"^\d+-(\d+) ", r"\1 ", q)
    if "&" in q:
        q = re.sub(r"^(\d+) ", "", q)
    return q


def is_suspicious_address(n: int | str, s: str):
    return bool(re.search(r"\b" + str(n) + r"(?:st|nd|rd|th)\b", s))


TYPES = {"intersection", "place_name", "address", "no location information", "not in NYC"}

if __name__ == "__main__":
    out = {}
    by_type = Counter[str]()
    n_dropped = 0
    for path in sys.argv[1:]:
        outputs = [json.loads(line) for line in open(path)]
        for r in outputs:
            id = r["custom_id"]
            response = r["response"]
            assert response["status_code"] == 200
            choices = response["body"]["choices"]
            assert len(choices) == 1
            data_str = choices[0]["message"]["content"]
            data: GptResponse = json.loads(data_str)
            # data = enforce_structure(data)
            assert "type" in data

            if data["type"] not in TYPES:
                n_dropped += 1
                sys.stderr.write(f"Weirdo alert! {id}: {data}\n")
                continue

            if data["type"] == "address" and not data["number"]:
                n_dropped += 1
                continue

            if data["type"] == "address" and is_suspicious_address(data["number"], data["street"]):
                # While possible, this seems to always be a mistake.
                # sys.stderr.write(f"Number and street are the same: {id}: {data}\n")
                n_dropped += 1
                continue

            by_type[data["type"]] += 1
            out[id] = data

    print(json.dumps(out, indent=2, sort_keys=True))
    sys.stderr.write(f"{len(out)} records\n")
    sys.stderr.write(f"{by_type.most_common()}\n")
    sys.stderr.write(f"{n_dropped} records dropped\n")
