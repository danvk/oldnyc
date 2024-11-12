from oldnyc.geocode.geocode_types import Coder, Locatable
from oldnyc.item import Item


class SpecialCasesCoder(Coder):
    def __init__(self):
        pass

    def codeRecord(self, r: Item):
        if r.title.startswith("Newspapers - China Daily News"):
            # The 2013 Milstein CSV file has a bunch of addresses along Mott Street for these.
            return Locatable(
                address="105 Mott Street, Manhattan, NY",
                source="China Daily News",
                type="address",
                data=(40.7173856, -73.9975334),
            )

        if r.title.startswith("Squatters Colony - Camp Thomas Paine."):
            # 733208f mentions 75th Street, but the 2013 CSV file has this address.
            return Locatable(
                address="West 70th Street and Riverside, Manhattan, N.Y.",
                source="Camp Thomas Paine",
                type="address",
                data=(40.779554, -73.988017),
            )

    def getLatLonFromLocatable(self, r, data):
        assert "data" in data
        return data["data"]

    def getLatLonFromGeocode(self, geocode, data, record):
        return None

    def name(self):
        return "special"
