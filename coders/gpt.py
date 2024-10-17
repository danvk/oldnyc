"""Coder for GPT-extracted location queries."""

import json
import sys

from coders.types import Coder, Locatable
from oldnyc.item import Item


class GptCoder(Coder):
    queries: dict[str, str]

    def __init__(self):
        with open("geogpt/geocodes.json") as f:
            self.queries = json.load(f)
        self.num_intersection = 0
        self.num_address = 0
        from coders.milstein import MilsteinCoder

        self.milstein = MilsteinCoder()

    def codeRecord(self, r: Item):
        # GPT location extractions are always based on record ID, not photo ID.
        id = r.id.split("-")[0]
        q = self.queries.get(id)
        if not q:
            return None

        is_intersection = "&" in q
        if is_intersection:
            self.num_intersection += 1
        else:
            self.num_address += 1
        return Locatable(
            address=q,
            source=q,
            # TODO: this could be improved
            type=(
                "intersection" if "&" in q else ["street_address", "premise"]
            ),  # , 'point_of_interest'],
        )

    def getLatLonFromGeocode(self, geocode, data, record: Item):
        result = self.milstein.getLatLonFromGeocode(geocode, data, record)
        if not result:
            sys.stderr.write(f"gpt geocode failed: {record.id}\n")
            sys.stderr.write(json.dumps(data) + "\n")
            sys.stderr.write(json.dumps(geocode) + "\n")
        else:
            tll = self.milstein._getLatLonFromGeocode(geocode, data)
            sys.stderr.write(f"gpt geocode success: {record.id} {tll}: {data}\n")
        return result

    def finalize(self):
        sys.stderr.write(f"GPT address:      {self.num_address}\n")
        sys.stderr.write(f"GPT intersection: {self.num_intersection}\n")

    def name(self):
        return "gpt"
