#!/usr/bin/env python
"""Generate a JSONL file of OCR tasks for the GPT batch API."""

import argparse
import base64
import json
import os
import sys


SYSTEM_PROMPT = """You'll be given an image containing text. Your goal is to transcribe
the text and determine whether the text is correctly oriented or rotated.

The text is written with a typewriter and describes a photograph taken in New York City,
likely in in the 1920s or 1930s. It likely includes street names, as well as the name
of the photographer, which might be "P. L. Sperr" or "Eugene L. Armbruster" or
"George L. Balgue". It's also likely to include a rights statement such as
"NO REPRODUCTIONS" or "MAY BE REPRODUCED". Make sure to include numbers like "(1)",
"(2)", etc. that appear in the image.

Respond with JSON in the following format:

{
  text: string;
  rotated: boolean;
}
"""


def get_image_base64(image_path: str) -> str:
    format = "jpeg"
    if ".png" in image_path:
        format = "png"
    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode("ascii")
    return f"data:image/{format};base64,{image_data}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a GPT batch JSONL file with OCR tasks."
    )
    parser.add_argument(
        "--model", default="gpt-4o-mini", choices=["gpt-4o", "gpt-4o-mini"]
    )
    parser.add_argument(
        "--image_directory",
        type=str,
        required=True,
        help="Path to directory containing image files. Must be named (id).png or (id).jpg.",
    )
    parser.add_argument(
        "id_files", type=str, nargs="+", help="File(s) containing image IDs"
    )
    parser.add_argument(
        "--temperature", type=float, default=0.0, help="GPT model temperature"
    )

    args = parser.parse_args()
    back_ids = [line.strip() for id_file in args.id_files for line in open(id_file)]
    assert back_ids

    num_dropped = 0
    tasks = []
    for back_id in back_ids:
        possible_paths = [
            os.path.join(args.image_directory, f"{back_id}.{ext}")
            for ext in ("jpg", "png")
        ]
        image_paths = [p for p in possible_paths if os.path.exists(p)]
        if len(image_paths) == 0:
            sys.stderr.write(
                f"Could not find image for {back_id}, tried: {possible_paths}\n"
            )
            num_dropped += 1
            continue
        elif len(image_paths) > 1:
            sys.stderr.write(f"Multiple image for {back_id}: {image_paths}\n")
            sys.exit(2)
        image_path = image_paths[0]

        task = {
            "custom_id": back_id,
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": args.model,
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
                                "image_url": {"url": get_image_base64(image_path)},
                            },
                        ],
                    },
                ],
                "temperature": args.temperature,
                "max_tokens": 2048,
                "top_p": 1,
                "frequency_penalty": 0,
                "presence_penalty": 0,
                "response_format": {
                    "type": "json_object",
                },
            },
        }
        tasks.append(task)
        print(json.dumps(task))

    if num_dropped:
        sys.stderr.write(f"Dropped {num_dropped} tasks.\n")
    sys.stderr.write(f"Wrote {len(tasks)} tasks\n")
