from dataclasses import dataclass
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

    back_id: Optional[str]
    """Photo ID for the back of the image (description); lowercase"""

    creator: Optional[str]
    """Name of the photographer"""

    subject: Subject

    back_text: Optional[str]
    """Backing text, as determined by OCR or manual transcription."""

    back_text_source: Optional[Literal["site", "gpt"]]

    address: Optional[str]
    """Possible address from original CSV. Unclear provenance."""

    source: str
    """Collection / sub-collection name"""
