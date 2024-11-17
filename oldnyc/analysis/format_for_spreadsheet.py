"""Take a list of IDs and output something to paste into Sheets."""

import fileinput
import json

from oldnyc.item import load_items


def main():
    ids = [line.strip() for line in fileinput.input()]
    items = load_items("data/images.ndjson")
    id_to_item = {r.id: r for r in items}

    gpt_geocodes = json.load(open("data/gpt-geocodes.json"))

    print("\t".join(["id", "url", "title", "alt_title", "back_text", "gpt_geocode"]))
    for id in ids:
        item = id_to_item[id]
        gpt = gpt_geocodes.get(id)
        print(
            "\t".join(
                [
                    id,
                    item.url,
                    item.title,
                    "\n".join(item.alt_title),
                    (item.back_text or "n/a").replace("\n", "|"),
                    json.dumps(gpt),
                ]
            )
        )


if __name__ == "__main__":
    main()
