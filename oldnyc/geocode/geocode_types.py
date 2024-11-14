# pyright: strict

from typing import Any, NotRequired, Protocol, TypedDict

from oldnyc.item import Item


class Locatable(TypedDict):
    address: str
    """Can be either a geolocatable address or @lat,lng"""
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
    def getLatLonFromLocatable(self, r: Item, data: Locatable) -> tuple[float, float] | None:
        """Extract a location from a Locatable, without going to Google."""
        ...

    def getLatLonFromGeocode(
        self, geocode: dict[str, Any], data: Locatable, record: Item
    ) -> tuple[float, float] | None:
        """Extract a location from a Google Maps geocoding API response."""
        ...

    def finalize(self) -> None: ...
