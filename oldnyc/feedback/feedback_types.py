"""Type definitions for user-feedback.json (Firebase dump)."""

from typing import NotRequired, Optional, TypedDict


class FeedbackMetadata(TypedDict):
    cookie: Optional[str]
    location: Optional[str]
    timestamp: int
    user_agent: str
    user_ip: Optional[str]


class TextFeedback(TypedDict):
    metadata: FeedbackMetadata
    text: str


class RotateFeedback(TypedDict):
    metadata: FeedbackMetadata
    rotate: int


class DateFeedback(TypedDict):
    metadata: FeedbackMetadata
    date: str


LocationFeedback = TypedDict(
    "LocationFeedback", {"metadata": FeedbackMetadata, "wrong-location": str}
)


Feedback = TypedDict(
    "Feedback",
    {
        "text": NotRequired[dict[str, TextFeedback]],
        "rotate": NotRequired[dict[str, RotateFeedback]],
        "date": NotRequired[dict[str, DateFeedback]],
    },
)


class FeedbackJson(TypedDict):
    feedback: dict[str, Feedback]
    """Map from photo_id (or back_id for text) -> Feedback"""
