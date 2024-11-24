"""Coder for GPT-extracted location queries."""

import json
import sys

from oldnyc.geocode.boroughs import guess_borough
from oldnyc.geocode.geocode_types import AddressLocation, Coder, IntersectionLocation
from oldnyc.geocode.geogpt.generate_batch import GptResponse
from oldnyc.item import Item


class GptCoder(Coder):
    queries: dict[str, list[GptResponse]]

    def __init__(self):
        with open("data/gpt-geocodes.json") as f:
            self.queries = json.load(f)
        self.num_intersection = 0
        self.num_address = 0
        self.num_poi = 0
        self.n_grid = 0
        self.n_grid_attempts = 0
        self.n_google_location = 0
        self.n_geocode_fail = 0
        self.n_boro_mismatch = 0

    def code_record(self, r: Item):
        # GPT location extractions are always based on record ID, not photo ID.
        id = r.id.split("-")[0]
        qs = self.queries.get(id)
        if not qs:
            return None
        return [locatable for q in qs if (locatable := self.code_one(r, q))]

    def code_one(self, r: Item, q: GptResponse):
        # sys.stderr.write(f"GPT location: {r.id} {q}\n")

        if q["type"] in ("no location information", "not in NYC"):
            return None

        boro = guess_borough(r)
        if boro is None:
            # sys.stderr.write(f"Failed to guess borough for {r.id}\n")
            boro = "New York"
        if q["type"] == "place_name":
            # TODO: look at these
            self.num_poi += 1
            return None
        elif q["type"] == "address":
            self.num_address += 1
            num = q["number"]
            street = q["street"]
            address = f"{num} {street}"
            return AddressLocation(
                source=address,
                boro=boro,
                num=num,
                street=street,
            )
        elif q["type"] == "intersection":
            self.num_intersection += 1
            str1 = q["street1"]
            str2 = q["street2"]
            (str1, str2) = sorted((str1, str2))  # try to increase cache coherence
            return IntersectionLocation(
                source=f"{str1} and {str2}",
                str1=str1,
                str2=str2,
                boro=boro,
            )
        # sys.stderr.write(f"GPT location: {r.id} {loc}\n")

    def finalize(self):
        sys.stderr.write(f"GPT POI:          {self.num_poi}\n")
        sys.stderr.write(f"GPT address:      {self.num_address}\n")
        sys.stderr.write(f"GPT intersection: {self.num_intersection}\n")

    def name(self):
        return "gpt"
