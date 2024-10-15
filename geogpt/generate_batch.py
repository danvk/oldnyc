#!/usr/bin/env python
"""Generate a batch of "extract geocodable text" tasks for GPT."""

import re
import sys
import json

from data.item import Item, load_items

# See https://cookbook.openai.com/examples/batch_processing
# TODO: Make more of an effort to get GPT the Borough (typically in SOURCE column of CSV)
SYSTEM_INSTRUCTIONS = """
Your goal is to extract location information from JSON describing a photograph taken
in New York City. The location information should be in the form of a query that can
be passed to the Google Maps geocoding API to get a latitude and longitude. It should
contain either cross streets, a place name, or an address. It should also contain the
borough that the photograph is in (Manhattan, Brooklyn, Queens, Bronx, Staten Island).
For example, "14th Street & 1st Avenue, Manhattan, NY".
If there's no location information in the photo, respond with "no location information".
If the photo is not in New York City, respond with "not in NYC".

Respond in JSON containing the following information:

{
  location: string; // Text to send into Google Maps geocoding API to get latitude and longitude of the image
} |
'no location information' | 'not in NYC';
"""


# MODEL = 'gpt-4o-mini'
MODEL = "gpt-4o"


def make_gpt_request(r: Item, model: str) -> dict:
    r = prep_data(r)
    gpt_data = {"title": r.title, "alt_title": r.alt_title}
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


def prep_data(data: Item):
    for field in ("title", "alt_title"):
        v = getattr(data, field)
        setattr(data, field, re.sub("^Richmond:", "Staten Island:", v))
    return v


if __name__ == "__main__":
    ids_file = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else MODEL
    ids = {line.strip() for line in open(ids_file)}

    records = load_items("data/items.ndjson")
    id_to_records = {r.id: r for r in records}

    for id in ids:
        print(json.dumps(make_gpt_request(id_to_records[id], model)))
