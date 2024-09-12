#!/usr/bin/env python
"""Generate a JSONL file of OCR tasks for the GPT batch API."""

import base64
import csv
import json
import os
import sys
import random

from record import Record


SYSTEM_PROMPT = '''You'll be given an image containing text. Your goal is to transcribe the text.

The text is written with a typewriter and describes a photograph taken in New York City,
likely in in the 1920s or 1930s. It likely includes street names, as well as the name
of the photographer, which might be "P. L. Sperr" or "Eugene L. Armbruster" or
"George L. Balgue". It's also likely to include a rights statement such as
"NO REPRODUCTIONS" or "MAY BE REPRODUCED". You'll also be given some JSON describing
that same photograph. It's likely to contain keywords and numbers that also appear
in the text.
'''


def get_image_base64(image_path: str) -> str:
    format = 'jpeg'
    if '.png' in image_path:
        format = 'png'
    with open(image_path, 'rb') as image_file:
        image_data = base64.b64encode(image_file.read()).decode('ascii')
    return f'data:image/{format};base64,{image_data}'


BACK_PAT = '/tmp/contrast/%s.png'


if __name__ == '__main__':
    back_ids_file = sys.argv[1]
    back_ids = [line.strip() for line in open(back_ids_file)]

    records: list[Record] = json.load(open('nyc/records.json'))
    back_id_to_record = {r['back_id']: r for r in records if r['back_id']}

    new_csv_rows = csv.DictReader(open('/Users/danvk/Downloads/Milstein_data_for_DV.csv'))
    front_id_to_new_csv = {
        row['image_id'].lower(): row
        for row in new_csv_rows
    }

    tasks = []
    for back_id in back_ids:
        r = back_id_to_record[back_id]
        csv_row = front_id_to_new_csv[r['id']]
        image_path = BACK_PAT % back_id
        if not os.path.exists(image_path):
            sys.stderr.write(f'Skipping {back_id}\n')
            continue
        metadata = {
            field: r[field]
            for field in ['title', 'alt_title', 'date']
            if r[field]
        }
        for k, v in csv_row.items():
            if k.startswith('subject/') and v:
                metadata[k] = v

        task = {
            "custom_id": back_id,
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": get_image_base64(image_path)
                                }
                            },
                            {
                                "type": "text",
                                "text": json.dumps(metadata),
                            },
                        ]
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 2048,
                "top_p": 1,
                "frequency_penalty": 0,
                "presence_penalty": 0,
                "response_format": {
                    "type": "text",
                }
            }
        }
        tasks.append(task)
        print(json.dumps(task))

    sys.stderr.write(f'Wrote {len(tasks)} tasks\n')
