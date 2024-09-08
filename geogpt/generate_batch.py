#!/usr/bin/env python
"""Generate a batch of "extract geocodable text" tasks for GPT."""

import sys
import json

from record import Record

PROMPT = """
Here's some JSON describing an image taken in New York City:

%s

What text can I feed into the Google Maps geocoding API to get a latitude and longitude
for this image? Respond in JSON matching the following TypeScript interface:

type LocatableText = {
  /** Text to send into Google Maps geocoding API to get latitude and longitude of the image */
  location: string;
} |
'no location information';
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
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": PROMPT % data,
                        },
                    ],
                }
            ],
            "temperature": 1,
            "max_tokens": 256,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0,
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
