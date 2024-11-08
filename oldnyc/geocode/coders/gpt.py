"""Coder for GPT-extracted location queries."""

import json
import sys

from oldnyc.geocode.coders.coder_utils import get_lat_lng_from_geocode
from oldnyc.geocode.geocode_types import Coder, Locatable
from oldnyc.geocode.geogpt.generate_batch import GptResponse
from oldnyc.item import Item


class GptCoder(Coder):
    queries: dict[str, GptResponse]

    def __init__(self):
        # with open("geogpt/geocodes.json") as f:
        # with open("/tmp/extracted-structure.json") as f:
        with open("/tmp/extracted-structure+text.json") as f:
            self.queries = json.load(f)
        self.num_intersection = 0
        self.num_address = 0
        self.num_poi = 0
        # TODO: can this be moved up top now?
        from oldnyc.geocode.coders.milstein import MilsteinCoder

        # Could also use extended-grid coder
        self.milstein = MilsteinCoder()

    def codeRecord(self, r: Item):
        # GPT location extractions are always based on record ID, not photo ID.
        id = r.id.split("-")[0]
        q = self.queries.get(id)
        if not q:
            return None
        sys.stderr.write(f"GPT location: {r.id} {q}\n")

        if q["type"] == "no_location":
            return None

        loc: Locatable | None = None
        boro = q["borough"]
        if q["type"] == "place_name":
            self.num_poi += 1
            return None
            # place = q["place_name"]
            # loc = {
            #     "address": f"{place}, {boro}, NY",
            #     "source": place,
            #     "type": ["point_of_interest", "premise"],
            # }
        elif q["type"] == "address":
            self.num_address += 1
            num = q["number"]
            street = q["street"]
            address = f"{num} {street}"
            loc = Locatable(
                address=f"{address}, {boro}, NY",
                source=address,
                type=["street_address", "premise"],
                data=q,
            )
        elif q["type"] == "intersection":
            self.num_intersection += 1
            street1 = q["street1"]
            street2 = q["street2"]
            loc = Locatable(
                address=f"{street1} & {street2}, {boro}, NY",
                source=f"{street1} & {street2}",
                type="intersection",
                data=q,
            )
        sys.stderr.write(f"GPT location: {r.id} {loc}\n")
        return loc

    def getLatLonFromGeocode(self, geocode, data, record: Item):
        result = self.milstein.getLatLonFromGeocode(geocode, data, record)
        if not result:
            sys.stderr.write(f"gpt geocode failed: {record.id}\n")
            sys.stderr.write(json.dumps(data) + "\n")
            sys.stderr.write(json.dumps(geocode) + "\n")
        else:
            tll = get_lat_lng_from_geocode(geocode, data)
            sys.stderr.write(f"gpt geocode success: {record.id} {tll}: {data}\n")
        return result

    def finalize(self):
        sys.stderr.write(f"GPT POI:          {self.num_poi}\n")
        sys.stderr.write(f"GPT address:      {self.num_address}\n")
        sys.stderr.write(f"GPT intersection: {self.num_intersection}\n")

    def name(self):
        return "gpt"
