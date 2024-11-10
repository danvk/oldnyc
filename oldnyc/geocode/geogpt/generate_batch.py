#!/usr/bin/env python
"""Generate a batch of "extract geocodable text" tasks for GPT."""

import dataclasses
import json
import re
import sys
from typing import Literal, TypedDict

from oldnyc.ingest.util import BOROUGHS
from oldnyc.item import Item, load_items

# See https://cookbook.openai.com/examples/batch_processing
SYSTEM_INSTRUCTIONS = """
Your goal is to extract location information from JSON describing a photograph taken in New York City. The location information should be either an intersection of two streets, a place name, or an address. It's also possible that there's no location information, or that the photo was not taken in New York City.

Respond in JSON matching the following TypeScript interface:

{
  type: "intersection";
  street1: string;
  street2: string;
} | {
  type: "address";
  number: number;
  street: string;
} | {
  type: "place_name";
  place_name: string;
} | {
  type: "no location information";
} | {
  type: "not in NYC";
}
"""


class GptIntersection(TypedDict):
    type: Literal["intersection"]
    street1: str
    street2: str


class GptAddress(TypedDict):
    type: Literal["address"]
    number: str
    street: str


class GptPlaceName(TypedDict):
    type: Literal["place_name"]
    place_name: str


class GptNoLocation(TypedDict):
    type: Literal["no location information"]


class GptNotNYC(TypedDict):
    type: Literal["not in NYC"]


GptResponse = GptIntersection | GptAddress | GptPlaceName | GptNoLocation | GptNotNYC

boroughs_pat = r"(?:Manhattan|Brooklyn|Queens|Bronx|Staten Island|Richmond)"

# Borough: str1 - str2
# Manhattan: 10th Street (East) - Broadway
boro_int = re.compile(rf"^({boroughs_pat}): ([^-:\[\]]+?) - ([^-:\[\]]+)$")


def make_gpt_request(r: Item, model: str) -> dict:
    r = prep_data(r)
    gpt_data = dataclasses.asdict(r)
    # These fields aren't useful for GPT
    gpt_data.pop("id", None)
    gpt_data.pop("uuid", None)
    gpt_data.pop("url", None)
    gpt_data.pop("photo_url", None)
    gpt_data.pop("back_text_source", None)
    gpt_data.pop("back_id", None)
    # borough = guess_borough(r)
    # if borough:
    #     gpt_data["borough"] = borough

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
        if item.address and item.address.endswith(full):
            return b
    for b in BOROUGHS:
        full = f"/ {b}"
        if item.source.endswith(full):
            return b
    return None


if __name__ == "__main__":
    if len(sys.argv) == 3:
        (ids_file, model) = sys.argv[1:]
    else:
        (model,) = sys.argv[1:]
        ids_file = None

    items = load_items("data/images.ndjson")
    ids = {line.strip() for line in open(ids_file)} if ids_file else (r.id for r in items)
    id_to_records = {r.id: r for r in items}

    for id in ids:
        item = id_to_records[id]
        # if boro_int.match(item.title):
        #     continue
        print(json.dumps(make_gpt_request(id_to_records[id], model)))
