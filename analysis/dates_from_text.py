"""Extract dates from backing text.

Sometimes there's a date in the text on the back of the card that's not in NYPL
metadata. We have to be careful to extract the date when the photo was taken, not
just some date mentioned in the photo.
"""

import datefinder


def match_full_date(text: str) -> list[str] | None:
    """Match any complete month day, year-style date."""
    return [
        date.strftime('%Y-%m-%d')
        for line in text.split('\n')
        for date in datefinder.find_dates(line, strict=True)
    ]


def get_dates_from_text(text: str):
    full_dates = match_full_date(text)
    if full_dates:
        return full_dates
