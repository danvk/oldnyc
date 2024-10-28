#!/usr/bin/env python
"""Extract photo ID -> geocodable string mapping from GPT JSONL output files."""

import json
import re
import sys

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


def enforce_structure(data: dict) -> dict:
    if "type" not in data:
        if "place_name" in data:
            data["type"] = "place_name"
        elif "street1" in data:
            data["type"] = "intersection"
        elif "number" in data:
            data["type"] = "address"

    dump = json.dumps(data)
    if (
        '"no location information"' in dump
        or '"unknown"' in dump
        or data.get("borough") not in BOROUGHS
    ):
        return {"type": "no_location"}

    assert data["type"] in ("place_name", "intersection", "address", "no_location")
    if data["type"] == "intersection":
        assert "street1" in data
        assert "street2" in data
        assert "borough" in data
    elif data["type"] == "address":
        assert "number" in data
        assert "street" in data
        assert "borough" in data
    elif data["type"] == "place_name":
        assert "place_name" in data
        assert "borough" in data

    return data


if __name__ == "__main__":
    out = {}
    n_unlocated = 0
    n_type = 0
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
            data = enforce_structure(data)
            if "type" in data:
                n_type += 1
            if data.get("type") == "no_location":
                n_unlocated += 1
            # gpt_location = data["location"]
            # if gpt_location in IGNORE_GEOCODES:
            #     continue
            out[id] = data

    print(json.dumps(out, indent=2, sort_keys=True))
    sys.stderr.write(f"{len(out)} records\n")
    sys.stderr.write(f"{n_type=}\n")
    sys.stderr.write(f"{n_unlocated=}\n")
