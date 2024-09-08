#!/usr/bin/env python
"""Generate a batch of "extract geocodable text" tasks for GPT."""

import sys
import json

from record import Record

# See https://cookbook.openai.com/examples/batch_processing
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
MODEL = 'gpt-4o'


def make_gpt_request(r: Record) -> dict:
    data = json.dumps(
        {
            "title": r["title"],
            "alt_title": r["alt_title"],
        }
    )
    return {
        "custom_id": r["id"],
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_INSTRUCTIONS,
                },
                {
                    "role": "user",
                    "content": data,
                }
            ],
            "temperature": 0.1,
            "response_format": {
                "type": "json_object"
            },
        },
    }


if __name__ == "__main__":
    ids_file = sys.argv[1]
    ids = {line.strip() for line in open(ids_file)}

    records: list[Record] = json.load(open("nyc/records.json"))
    id_to_records = {r["id"]: r for r in records}

    for id in ids:
        print(json.dumps(make_gpt_request(id_to_records[id])))
