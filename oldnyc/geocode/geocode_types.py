# pyright: strict

from dataclasses import dataclass
from typing import Protocol

from oldnyc.item import Item

Point = tuple[float, float]


@dataclass
class IntersectionLocation:
    str1: str
    str2: str
    boro: str
    source: str


@dataclass
class AddressLocation:
    num: str
    street: str
    boro: str
    source: str


@dataclass
class LatLngLocation:
    lat: float
    lng: float
    source: str


Locatable = IntersectionLocation | AddressLocation | LatLngLocation


class Coder(Protocol):
    def code_record(self, r: Item) -> Locatable | None: ...

    def name(self) -> str: ...

    def finalize(self) -> None: ...
