#!/usr/bin/env python
"""Review GPT's extracted location strings."""

import json
import random
import sys

from oldnyc.geocode.geogpt.generate_batch import GptResponse
from oldnyc.item import load_items


def scrub(txt: str) -> str:
    return txt.replace(".", "")


if __name__ == "__main__":
    input_file, output_file = sys.argv[1:]

    input_data = [json.loads(line) for line in open(input_file)]
    id_to_input = {
        input["custom_id"]: json.loads(input["body"]["messages"][1]["content"])
        for input in input_data
    }

    records = load_items("data/images.ndjson")
    id_to_records = {r.id: r for r in records}

    output_data = [json.loads(line) for line in open(output_file)]
    id_to_output = {r["custom_id"]: r for r in output_data}

    photo_ids = [*sorted(id_to_input.keys())]
    random.shuffle(photo_ids)

    n_matches = 0
    for photo_id in photo_ids:
        input = id_to_input[photo_id]
        r = id_to_output[photo_id]
        response = r["response"]
        assert response["status_code"] == 200
        choices = response["body"]["choices"]
        assert len(choices) == 1
        data_str = choices[0]["message"]["content"]
        data: GptResponse = json.loads(data_str)
        # gpt_location = data["location"]

        csv_location = id_to_records[photo_id].address
        # is_match = scrub(gpt_location) == scrub(csv_location or "")

        # if not is_match:
        print("Photo ID:", photo_id)
        print("Input:", json.dumps(input, indent=2))
        print("GPT:  ", data)
        print("CSV:  ", csv_location)
        # print("Match:", is_match)

        print("\n\n----\n\n")

        # if is_match:
        #     n_matches += 1

    print(f"Exact matches: {n_matches} / {len(output_data)}")
