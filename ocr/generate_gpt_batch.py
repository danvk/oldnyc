#!/usr/bin/env python
"""Generate a JSONL file of OCR tasks for the GPT batch API."""

import base64
import json
import os
import sys


SYSTEM_PROMPT = '''You'll be given an image containing text. Your goal is to transcribe
the text and determine whether the text is correctly oriented or rotated.

The text is written with a typewriter and describes a photograph taken in New York City,
likely in in the 1920s or 1930s. It likely includes street names, as well as the name
of the photographer, which might be "P. L. Sperr" or "Eugene L. Armbruster" or
"George L. Balgue". It's also likely to include a rights statement such as
"NO REPRODUCTIONS" or "MAY BE REPRODUCED".

Respond with JSON in the following format:

{
  text: string;
  rotated: boolean;
}
'''


def get_image_base64(image_path: str) -> str:
    format = 'jpeg'
    if '.png' in image_path:
        format = 'png'
    with open(image_path, 'rb') as image_file:
        image_data = base64.b64encode(image_file.read()).decode('ascii')
    return f'data:image/{format};base64,{image_data}'


BACK_PAT = '/tmp/contrast-1500/%s.jpg'


if __name__ == '__main__':
    back_ids_file = sys.argv[1]
    back_ids = [line.strip() for line in open(back_ids_file)]

    tasks = []
    for back_id in back_ids:
        image_path = BACK_PAT % back_id
        if not os.path.exists(image_path):
            sys.stderr.write(f'Skipping {back_id}\n')
            continue

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
                        ]
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 2048,
                "top_p": 1,
                "frequency_penalty": 0,
                "presence_penalty": 0,
                "response_format": {
                    "type": "json_object",
                }
            }
        }
        tasks.append(task)
        print(json.dumps(task))

    sys.stderr.write(f'Wrote {len(tasks)} tasks\n')
