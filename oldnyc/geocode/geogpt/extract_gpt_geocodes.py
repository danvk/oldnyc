#!/usr/bin/env python
"""Extract photo ID -> geocodable string mapping from GPT JSONL output files."""

import json
import re
import sys
from collections import Counter

from oldnyc.geocode.geogpt.generate_batch import GptResponse
from oldnyc.ingest.util import BOROUGHS

IGNORE_GEOCODES = {
    "not in NYC",
    "no location information",
}


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


TYPES = {"intersection", "place_name", "address", "no location information", "not in NYC"}

if __name__ == "__main__":
    out = {}
    by_type = Counter[str]()
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
                sys.stderr.write(f"Weirdo alert! {id}: {data}\n")
                continue

            by_type[data["type"]] += 1
            out[id] = data

    print(json.dumps(out, indent=2, sort_keys=True))
    sys.stderr.write(f"{len(out)} records\n")
    sys.stderr.write(f"{by_type.most_common()}\n")
