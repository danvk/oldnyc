from typing import NotRequired, Optional, TypedDict


class LatLon(TypedDict):
    lat: float
    lon: float


class DateFields(TypedDict):
    date_source: str
    date: str
    years: list[str]
    dates_from_text: NotRequired[list[str]]


class SiteItem(DateFields):
    folder: Optional[str]
    width: int
    height: int
    title: str
    thumb_url: str
    image_url: str
    nypl_url: str
    text: Optional[str]
    original_title: NotRequired[str]
    rotation: NotRequired[int]


class SitePhoto(SiteItem):
    """Type of the photos in data.json"""

    photo_id: str
    location: LatLon


class SiteResponse(SiteItem):
    """Type of the entries in by-location/*.json"""

    id: str


class Timestamps(TypedDict):
    timestamp: str
    rotation_time: str
    ocr_time: str
    ocr_ms: int


class SiteJson(Timestamps):
    photos: list[SitePhoto]


class PopularPhoto(TypedDict):
    """Type for popular-photos.js"""

    date: str
    loc: str
    height: int
    id: str
    desc: str
