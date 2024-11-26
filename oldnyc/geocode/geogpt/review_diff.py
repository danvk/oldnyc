"""Generate localturk CSV file to review a GeoJSON diff related to geogpt changes."""

import csv
import dataclasses
import json
import sys

from oldnyc.geocode.geogpt.generate_batch import GptResponse
from oldnyc.item import load_items
from oldnyc.util import encode_json_base64


def main():
    (tsv_file, old_gpt_file, new_gpt_file) = sys.argv[1:]

    old_gpt: dict[str, GptResponse] = json.load(open(old_gpt_file))
    new_gpt: dict[str, GptResponse] = json.load(open(new_gpt_file))
    diffs = [*csv.DictReader(open(tsv_file), delimiter="\t")]
    items = load_items("data/images.ndjson")
    id_to_item = {item.id: item for item in items}

    # ID	Title	Old LatLng	Old Coder	New LatLng	New Coder	Move Str
    out = csv.DictWriter(
        sys.stdout,
        fieldnames=[
            "id",
            "item_jsonb64",
            "title",
            "nypl_url",
            "photo_url",
            "old_latlng",
            "old_coder",
            "new_latlng",
            "new_coder",
            "move_str",
            "old_gpt_jsonb64",
            "new_gpt_jsonb64",
        ],
    )
    out.writeheader()
    for diff in diffs:
        id = diff["ID"]
        item = id_to_item[id]
        old_gpt_data = old_gpt.get(id)
        new_gpt_data = new_gpt.get(id)
        out.writerow(
            {
                "id": id,
                "item_jsonb64": encode_json_base64(dataclasses.asdict(item)),
                "title": item.title,
                "nypl_url": item.url,
                "photo_url": item.photo_url,
                "old_latlng": diff["Old LatLng"],
                "old_coder": diff["Old Coder"],
                "new_latlng": diff["New LatLng"],
                "new_coder": diff["New Coder"],
                "move_str": diff["Move Str"],
                "old_gpt_jsonb64": encode_json_base64(old_gpt_data),
                "new_gpt_jsonb64": encode_json_base64(new_gpt_data),
            }
        )


if __name__ == "__main__":
    main()
