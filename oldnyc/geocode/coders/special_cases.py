import sys
from collections import Counter

from oldnyc.geocode.geocode_types import Coder, LatLngLocation
from oldnyc.item import Item


class SpecialCasesCoder(Coder):
    def __init__(self):
        self.counts = Counter[str]()

    def code_record(self, r: Item):
        if r.title.startswith("Newspapers - China Daily News"):
            # The 2013 Milstein CSV file has a bunch of addresses along Mott Street for these.
            self.counts["China Daily News"] += 1
            return [
                LatLngLocation(
                    # address="105 Mott Street, Manhattan, NY",
                    source="China Daily News",
                    lat=40.7173856,
                    lng=-73.9975334,
                )
            ]

        if r.title.startswith("Squatters Colony - Camp Thomas Paine."):
            # 733208f mentions 75th Street, but the 2013 CSV file has this address.
            self.counts["Squatters: Camp Thomas Paine"] += 1
            return [
                LatLngLocation(
                    # address="West 70th Street and Riverside, Manhattan, N.Y.",
                    source="Camp Thomas Paine",
                    lat=40.779554,
                    lng=-73.988017,
                )
            ]

        if "Cathedral of St. John the Divine (New York, N.Y.)" in r.subject.name:
            self.counts["St. John the Divine"] += 1
            return [
                LatLngLocation(
                    # address="Cathedral of St. John the Divine, New York, N.Y.",
                    source="Cathedral of St. John the Divine",
                    lat=40.8038356,
                    lng=-73.9618754,
                )
            ]

        if "Mount Sinai Hospital (New York, N.Y.)" in r.subject.name:
            self.counts["Mt. Sinai"] += 1
            return [
                LatLngLocation(
                    # address="Mount Sinai Hospital, New York, N.Y.)",
                    source="Mount Sinai Hospital",
                    lat=40.789196,
                    lng=-73.954817,
                )
            ]

        titles = [r.title] + r.alt_title
        for title in titles:
            if title.startswith("Manhattan: Columbus Circle"):
                self.counts["Columbus Circle"] += 1
                return [
                    LatLngLocation(
                        # address="Columbus Circle, Manhattan, N.Y.",
                        source="Columbus Circle",
                        lat=40.76808,
                        lng=-73.981896,
                    )
                ]

    def finalize(self):
        sys.stderr.write(f"Special cases: {self.counts.most_common()}\n")

    def name(self):
        return "special"
