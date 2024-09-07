#!/usr/bin/env python
"""Generate a JSONL file of OCR tasks for the GPT batch API."""

import base64
import json
import os
import sys
import random

from record import Record


PROMPT = '''Transcribe the text in this image. The image has a dark border
surrounding a white piece of paper. Focus on the white paper. The text is
written with a typewriter and describes a photograph taken in New York City,
likely in in the 1920s or 1930s. It likely includes street names, as well as
the name of the photographer, which might be "P. L. Sperr" or
"Eugene L. Armbruster" or "George L. Balgue".
It's also likely to include a rights statement such as
"NO REPRODUCTIONS", "MAY BE REPRODUCED" or "CREDIT LINE IMPERATIVE".

Here's some JSON describing this image:

%s
'''


def get_jpeg_base64(image_path: str) -> str:
    with open(image_path, 'rb') as image_file:
        image_data = base64.b64encode(image_file.read()).decode('ascii')
    return f'data:image/jpeg;base64,{image_data}'


if __name__ == '__main__':
    n = int(sys.argv[1])
    back_pat = sys.argv[2]
    # photo_ids = set(sys.argv[2].split(',')) if len(sys.argv) > 2 else None
    photo_ids = None
    records: list[Record] = json.load(open('nyc/records.json'))
    random.shuffle(records)
    tasks = []
    for r in records:
        photo_id = r['id']
        if photo_ids and photo_id not in photo_ids:
            continue
        back = r['back_id']
        if not back:
            continue
        # f'/Users/danvk/Documents/oldnyc/images/{back}.jpg'
        image_path = back_pat % back
        if not os.path.exists(image_path):
            continue
        try:
            metadata = {
                field: r[field]
                for field in ['title', 'alt_title', 'date']
                if r[field]
            }
        except KeyError as e:
            print(r)
            raise e

        task = {
            "custom_id": photo_id,
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": "gpt-4o-mini",
                "messages": [
                    {
                    "role": "user",
                    "content": [
                        {
                        "type": "text",
                        "text": PROMPT % metadata,
                        },
                        {
                        "type": "image_url",
                        "image_url": {
                            "url": get_jpeg_base64(image_path)
                        }
                        }
                    ]
                    }
                ],
                "temperature": 1,
                "max_tokens": 256,
                "top_p": 1,
                "frequency_penalty": 0,
                "presence_penalty": 0,
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "ocr_output",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "text": {
                                "type": "string"
                                }
                            },
                            "required": ["text"],
                            "additionalProperties": False
                        },
                        "strict": True
                    }
                }
            }
        }
        tasks.append(task)
        print(json.dumps(task))
        if len(tasks) >= n:
            break
    sys.stderr.write(f'Wrote {len(tasks)} tasks\n')
