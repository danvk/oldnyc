from dataclasses import dataclass
import json
from typing import Literal, Optional

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Subject:
    name: list[str]
    """If set, the name of the subject, e.g. "Battery Park"."""

    temporal: list[str]
    """Sometimes has a decade"""

    geographic: list[str]
    """A comma-separated jumble of geographic information"""

    topic: list[str]
    """Broad topics like "buildings" or "directories"."""


@dataclass_json
@dataclass
class Item:
    id: str
    """NYPL Image ID; lowercase"""

    uuid: str
    """Item UUID (this is different than the UUID in the URL)"""

    url: str
    """Digital Collections URL for item"""

    date: str
    """raw date string from NYPL"""

    title: str
    alt_title: Optional[str]

    creator: Optional[str]
    """Name of the photographer"""

    subject: Subject

    back_id: Optional[str]
    """Photo ID for the back of the image (description); lowercase"""

    back_text: Optional[str]
    """Backing text, as determined by OCR or manual transcription."""

    back_text_source: Optional[Literal["site", "gpt"]]

    address: Optional[str]
    """Possible address from original CSV. Unclear provenance."""

    source: str
    """Collection / sub-collection name"""


def json_to_item(txt: str) -> Item:
    # This is much faster than using dataclasses_json if you need subject.
    data = json.loads(txt)
    item = Item(**data)
    item.subject = Subject(**data["subject"])
    return item


def blank_item() -> Item:
    return Item(
        id="PHOTO_ID",
        uuid="12345678-1234-1234-1234-1234567890ab",
        url="https://digitalcollections.nypl.org/",
        date="",
        title="",
        alt_title=None,
        creator=None,
        back_id=None,
        back_text_source=None,
        back_text=None,
        address=None,
        subject=Subject(name=[], temporal=[], geographic=[], topic=[]),
        source="Milstein",
    )
