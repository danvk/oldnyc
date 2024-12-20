#!/usr/bin/env python
"""Gather output from a GPT batch JSONL into a JSON file for evaluation."""

import json
import sys

if __name__ == "__main__":
    mapping = {}
    for gpt_output_file in sys.argv[1:]:
        # Prefix file with "!" to indicate that images were manually rotated.
        ignore_rotation = False
        if gpt_output_file.startswith("!"):
            ignore_rotation = True
            gpt_output_file = gpt_output_file[1:]

        gpt_data = [json.loads(line) for line in open(gpt_output_file)]

        for r in gpt_data:
            back_id = r["custom_id"]
            response = r["response"]
            assert response["status_code"] == 200
            choices = response["body"]["choices"]
            assert len(choices) == 1
            data_str = choices[0]["message"]["content"]
            try:
                data = json.loads(data_str)
            except json.decoder.JSONDecodeError:
                sys.stderr.write(f"{back_id}\tmalformed JSON\n")
                continue
                # This can all be patched by adding a trailing '"}', but the
                # OCR text generally has other issues and should be dropped.
                # data_str += '"}'
                # data = json.loads(data_str)
            rotated = not ignore_rotation and data.get("rotated")
            gpt_text = data["text"]
            # if rotated:
            #     sys.stderr.write(f"{back_id}\trotated\n")
            has_existing = back_id in mapping
            existing_rotated = has_existing and mapping[back_id]["text"] == "(rotated)"

            # overwrite existing entries, but prefer non-rotated OCR
            if not (back_id in mapping and rotated) or (existing_rotated and not rotated):
                out = {
                    "text": gpt_text if not rotated else "(rotated)",
                }
                mapping[back_id] = out

    for back_id, out in mapping.items():
        if out["text"] == "(rotated)":
            sys.stderr.write(f"{back_id}\trotated\n")

    sys.stderr.write(f"Writing {len(mapping)} records.\n")
    print(json.dumps(mapping, indent=2))
