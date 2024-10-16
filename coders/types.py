# pyright: strict

from typing import Any, Optional, Protocol, TypedDict

from data.item import Item


class Location(TypedDict):
    address: str
    lat: float
    lon: float


class Locatable(TypedDict):
    address: str
    lat: Optional[float]
    lon: Optional[float]
    source: str
    type: str  # 'point_of_interest', 'intersection'


class Coder(Protocol):
    def codeRecord(self, r: Item) -> Locatable: ...

    def name(self) -> str: ...
    def getLatLonFromGeocode(
        self, geocode: dict[str, Any], data: Locatable, record: Item
    ) -> tuple[float, float] | None: ...
    def finalize(self) -> None: ...
