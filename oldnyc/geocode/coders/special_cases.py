import sys
from collections import Counter

import pygeojson

from oldnyc.geocode.geocode_types import Coder, LatLngLocation, Point
from oldnyc.item import Item


class SpecialCasesCoder(Coder):
    def __init__(self):
        self.counts = Counter[str]()

    def code_record(self, r: Item):
        loc = self.code_one_record(r)
        if loc:
            return [loc]

    def code_one_record(self, r: Item):
        if r.title.startswith("Newspapers - China Daily News"):
            # The 2013 Milstein CSV file has a bunch of addresses along Mott Street for these.
            self.counts["China Daily News"] += 1
            return LatLngLocation(
                # address="105 Mott Street, Manhattan, NY",
                source="China Daily News",
                lat=40.7173856,
                lng=-73.9975334,
            )

        if r.title.startswith("Squatters Colony - Camp Thomas Paine."):
            # 733208f mentions 75th Street, but the 2013 CSV file has this address.
            self.counts["Squatters: Camp Thomas Paine"] += 1
            return LatLngLocation(
                # address="West 70th Street and Riverside, Manhattan, N.Y.",
                source="Camp Thomas Paine",
                lat=40.779554,
                lng=-73.988017,
            )

        if "Cathedral of St. John the Divine (New York, N.Y.)" in r.subject.name:
            self.counts["St. John the Divine"] += 1
            return LatLngLocation(
                # address="Cathedral of St. John the Divine, New York, N.Y.",
                source="Cathedral of St. John the Divine",
                lat=40.8038356,
                lng=-73.9618754,
            )

        if "Mount Sinai Hospital (New York, N.Y.)" in r.subject.name:
            self.counts["Mt. Sinai"] += 1
            return LatLngLocation(
                # address="Mount Sinai Hospital, New York, N.Y.)",
                source="Mount Sinai Hospital",
                lat=40.789196,
                lng=-73.954817,
            )

        titles = [r.title] + r.alt_title
        for title in titles:
            if title.startswith("Manhattan: Columbus Circle"):
                self.counts["Columbus Circle"] += 1
                return LatLngLocation(
                    # address="Columbus Circle, Manhattan, N.Y.",
                    source="Columbus Circle",
                    lat=40.76808,
                    lng=-73.981896,
                )

    def finalize(self):
        sys.stderr.write(f"Special cases: {self.counts.most_common()}\n")

    def name(self):
        return "special"


UNLOCATED_FIFTH_AVE = {
    "1113223",  # cover photo
    "1113224",  # title page
    "1113270",  # misfiled?
    "1113303",  # index of merchants
    "1113304",
    "1113305",
    "1113306",
}


class FifthAvenueCoder(Coder):
    """Special casing for "Fifth Avenue, Start to Finish" collection.

    This is an awkward fit for other coders because one cross street (Fifth Avenue)
    is only mentioned as part of the source, and all the streets mentioned in the
    title are crossing streets or addresses on Fifth Avenue.

    It's also easy to geocode because of a previous NYPL Labs project:
    https://github.com/NYPL-publicdomain/fifth-avenue
    """

    def __init__(self):
        self.id_to_point = dict[str, Point]()
        self.claimed = set[str]()
        fc = pygeojson.load_feature_collection(open("data/originals/fifth-avenue.geojson"))
        for f in fc.features:
            assert f.geometry
            assert isinstance(f.geometry, pygeojson.GeometryCollection)
            assert len(f.geometry.geometries) == 2
            g = f.geometry.geometries[0]
            assert isinstance(g, pygeojson.Point)
            # other geometry is a LineString indicating field of view
            id = f.properties["data"]["imageId"]
            lng, lat = g.coordinates[:2]
            self.id_to_point[id] = (lat, lng)

    def code_record(self, r: Item):
        loc = self.code_one_record(r)
        if loc:
            return [loc]

    def code_one_record(self, r: Item):
        if r.source != "Fifth Avenue, New York, from start to finish":
            return None
        if r.id in UNLOCATED_FIFTH_AVE:
            return None
        pt = self.id_to_point[r.id]
        self.claimed.add(r.id)
        return LatLngLocation(lat=pt[0], lng=pt[1], source="Fifth Avenue") if pt else None

    def finalize(self):
        sys.stderr.write(f"Fifth Avenue: {len(self.claimed)} claimed\n")
        # assert len(self.claimed) == len(self.id_to_point)

    def name(self):
        return "fifth"
