"""Coder for GPT-extracted location queries."""

import json
import sys

from oldnyc.geocode import grid
from oldnyc.geocode.boroughs import guess_borough, point_to_borough
from oldnyc.geocode.coders.coder_utils import get_lat_lng_from_geocode
from oldnyc.geocode.geocode_types import Coder, Locatable
from oldnyc.geocode.geogpt.generate_batch import GptResponse
from oldnyc.item import Item


class GptCoder(Coder):
    queries: dict[str, GptResponse]

    def __init__(self):
        with open("data/gpt-geocodes.json") as f:
            self.queries = json.load(f)
        self.num_intersection = 0
        self.num_address = 0
        self.num_poi = 0
        self.n_grid = 0
        self.n_google_location = 0
        self.n_geocode_fail = 0
        self.n_boro_mismatch = 0

    def codeRecord(self, r: Item):
        # GPT location extractions are always based on record ID, not photo ID.
        id = r.id.split("-")[0]
        q = self.queries.get(id)
        if not q:
            return None
        # sys.stderr.write(f"GPT location: {r.id} {q}\n")

        if q["type"] in ("no location information", "not in NYC"):
            return None

        loc: Locatable | None = None
        boro = guess_borough(r)
        if boro is None:
            # sys.stderr.write(f"Failed to guess borough for {r.id}\n")
            boro = "New York"
        if q["type"] == "place_name":
            self.num_poi += 1
            return None
        elif q["type"] == "address":
            self.num_address += 1
            num = q["number"]
            street = q["street"]
            address = f"{num} {street}"
            loc = Locatable(
                address=f"{address}, {boro}, NY",
                source=address,
                type=["street_address", "premise"],
                data={**q, "boro": boro},
            )
        elif q["type"] == "intersection":
            self.num_intersection += 1
            str1 = q["street1"]
            str2 = q["street2"]
            (str1, str2) = sorted((str1, str2))  # try to increase cache coherence
            loc = Locatable(
                address=f"{str1} and {str2}, {boro}, NY",
                source=f"{str1} and {str2}",
                type="intersection",
                data=(str1, str2, boro),
            )
        # sys.stderr.write(f"GPT location: {r.id} {loc}\n")
        return loc

    # TODO: next two methods are nearly identical to those in title_pattern.py
    def getLatLonFromLocatable(self, r, data):
        if data["type"] != "intersection":
            return None
        assert "data" in data
        ssb: tuple[str, str, str] = data["data"]
        (str1, str2, boro) = ssb
        if boro != "Manhattan" and boro != "New York":
            return None
        try:
            latlon = grid.geocode_intersection(str1, str2, r.id)
            if latlon:
                self.n_grid += 1
                lat, lng = latlon
                return round(float(lat), 7), round(float(lng), 7)  # they're numpy floats
        except ValueError:
            pass

    def getLatLonFromGeocode(self, geocode, data, record):
        assert "data" in data
        boro = None
        if data["type"] == "intersection":
            ssb: tuple[str, str, str] = data["data"]
            (str1, str2, boro) = ssb
        elif "street_address" in data["type"]:
            boro = data["data"]["boro"]

        tlatlng = get_lat_lng_from_geocode(geocode, data)
        if not tlatlng:
            self.n_geocode_fail += 1
            return None
        _, lat, lng = tlatlng
        geocode_boro = point_to_borough(lat, lng)
        if geocode_boro != boro and not (boro == "New York" and geocode_boro == "Manhattan"):
            self.n_boro_mismatch += 1
            sys.stderr.write(
                f'gpt Borough mismatch: {record.id}: {data["source"]} geocoded to {geocode_boro} not {boro}\n'
            )
            return None
        self.n_google_location += 1
        return (lat, lng)

    def finalize(self):
        sys.stderr.write(f"GPT POI:          {self.num_poi}\n")
        sys.stderr.write(f"GPT address:      {self.num_address}\n")
        sys.stderr.write(f"GPT intersection: {self.num_intersection}\n")

        sys.stderr.write("GPT geocoding results:\n")
        sys.stderr.write(f"            grid: {self.n_grid}\n")
        sys.stderr.write(f"          google: {self.n_google_location}\n")
        sys.stderr.write(f"   boro mismatch: {self.n_boro_mismatch}\n")
        sys.stderr.write(f"        failures: {self.n_geocode_fail}\n")

    def name(self):
        return "gpt"
