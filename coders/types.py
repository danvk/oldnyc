from typing import TypedDict, Protocol

from data.item import Item


class Location(TypedDict):
    address: str
    lat: float
    lon: float


class Locatable(TypedDict):
    address: str
    source: str
    type: str  # 'point_of_interest', 'intersection'


class Coder(Protocol):

    def codeRecord(self, r: Item) -> Locatable: ...

    def name(self) -> str: ...
    def getLatLonFromGeocode(
        self, geocode: dict, data
    ) -> tuple[float, float] | None: ...
    def finalize(self) -> None: ...
