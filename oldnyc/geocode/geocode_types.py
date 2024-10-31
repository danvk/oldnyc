# pyright: strict

from typing import Any, NotRequired, Protocol, TypedDict

from oldnyc.item import Item


class Location(TypedDict):
    address: str
    lat: float
    lon: float


class Locatable(TypedDict):
    address: str
    lat: NotRequired[float]
    lon: NotRequired[float]
    grid: NotRequired[str]
    subject: NotRequired[str]
    source: str
    type: str | list[str]  # 'point_of_interest', 'intersection'
    data: NotRequired[Any]


class Coder(Protocol):
    def codeRecord(self, r: Item) -> Locatable | None: ...

    def name(self) -> str: ...
    def getLatLonFromGeocode(
        self, geocode: dict[str, Any], data: Locatable, record: Item
    ) -> tuple[float, float] | None: ...
    def finalize(self) -> None: ...
