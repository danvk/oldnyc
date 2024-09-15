#!/usr/bin/env python
"""Extract photo ID -> geocodable string mapping from GPT JSONL output files."""

import json
import re
import sys


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


if __name__ == "__main__":
    out = {}
    for path in sys.argv[1:]:
        outputs = [json.loads(line) for line in open(path)]
        for r in outputs:
            id = r["custom_id"]
            response = r["response"]
            assert response["status_code"] == 200
            choices = response["body"]["choices"]
            assert len(choices) == 1
            data_str = choices[0]["message"]["content"]
            data = json.loads(data_str)
            gpt_location = data["location"]
            if gpt_location in IGNORE_GEOCODES:
                continue
            out[id] = patch_query(gpt_location)

    print(json.dumps(out, indent=2, sort_keys=True))
