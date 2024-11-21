#!/usr/bin/env python
"""Generate a batch of "extract geocodable text" tasks for GPT."""

import argparse
import dataclasses
import json
import re
import sys
from typing import Literal, TypedDict

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
    gpt_data.pop("address", None)
    gpt_data.pop("creator", None)
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate batch files for geocode extraction")
    parser.add_argument("--model", default="gpt-4o", help="GPT model to use")
    parser.add_argument("--ids_file", type=str, help="File containing IDs to process, one per line")
    parser.add_argument("--ids_filter", type=str, help="Comma-separated list of IDs to process")
    parser.add_argument(
        "--copy-paste",
        action="store_true",
        help="Output in copy-paste format for OpenAI Playground",
    )
    args = parser.parse_args()
    assert not (
        args.ids_file and args.ids_filter
    ), "Specify either --ids_file or --ids_filter, not both"

    items = load_items("data/images.ndjson")
    if args.ids_file:
        ids = {line.strip() for line in open(args.ids_file)}
    elif args.ids_filter:
        ids = args.ids_filter.split(",")
    else:
        ids = (r.id for r in items)

    id_to_records = {r.id: r for r in items}

    for id in ids:
        item = id_to_records[id]
        req = make_gpt_request(item, args.model)
        if args.copy_paste:
            for message in req["body"]["messages"]:
                print(message["content"])
        else:
            print(json.dumps(req))
