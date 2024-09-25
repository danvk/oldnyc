#!/usr/bin/env python
"""Generate a batch of "extract geocodable text" tasks for GPT."""

import dataclasses
import re
import sys
import json

from data.item import Item, json_to_item
from data.util import BOROUGHS

# See https://cookbook.openai.com/examples/batch_processing
SYSTEM_INSTRUCTIONS = """
Your goal is to extract location information from JSON describing a photograph taken
in New York City. The location information should be either an intersection of two streets,
a place name, or an address. It should also contain the borough that the photograph is in
(Manhattan, Brooklyn, Queens, Bronx, Staten Island).
If there's no location information in the photo, respond with "no location information".
If the photo is not in New York City, respond with "not in NYC".

Respond in JSON containing the following information:

{
  type: "intersection";
  street1: string;
  street2: string;
  borough: "Manhattan" | "Brooklyn" | "Queens" | "Bronx" | "Staten Island"
} | {
  type: "address";
  number: number;
  street: number;
  borough: "Manhattan" | "Brooklyn" | "Queens" | "Bronx" | "Staten Island"
} | {
  place_name: string;
  borough: "Manhattan" | "Brooklyn" | "Queens" | "Bronx" | "Staten Island"
}
'no location information' | 'not in NYC';
"""

# TODO: In Queens, addresses might be strings


def make_gpt_request(r: Item, model: str) -> dict:
    r = prep_data(r)
    gpt_data = {
        "title": r.title,
        "alt_title": r.alt_title,
    }
    borough = guess_borough(r)
    if borough:
        gpt_data["borough"] = borough

    data = json.dumps(gpt_data)
    return {
        "custom_id": r.id,
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_INSTRUCTIONS,
                },
                {
                    "role": "user",
                    "content": data,
                },
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        },
    }


def prep_field(txt: str | None) -> str | None:
    if not txt:
        return txt
    return re.sub("^Richmond:", "Staten Island:", txt)


def prep_data(item: Item):
    return dataclasses.replace(
        item,
        title=prep_field(item.title),
        alt_title=[prep_field(t) for t in item.alt_title] if item.alt_title else None,
    )


def guess_borough(item: Item):
    for b in BOROUGHS:
        full = f"{b} (New York, N.Y.)"
        if full in item.subject.geographic:
            return b
    for b in BOROUGHS:
        full = f"{b}, NY"
        if item.address.endswith(full):
            return b
    for b in BOROUGHS:
        full = f"/ {b}"
        if item.source.endswith(full):
            return b
    return None


if __name__ == "__main__":
    (ids_file, model) = sys.argv[1:]
    ids = {line.strip() for line in open(ids_file)}

    items = [json_to_item(line) for line in open("data/images.ndjson")]
    id_to_records = {r.id: r for r in items}

    for id in ids:
        print(json.dumps(make_gpt_request(id_to_records[id], model)))
