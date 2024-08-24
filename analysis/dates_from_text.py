"""Extract dates from backing text.

Sometimes there's a date in the text on the back of the card that's not in NYPL
metadata. We have to be careful to extract the date when the photo was taken, not
just some date mentioned in the photo.
"""

import re

import datefinder


def match_full_date(text: str) -> list[str] | None:
    """Match any complete month day, year-style date."""
    return [
        date.strftime('%Y-%m-%d')
        for line in text.split('\n')
        for date in datefinder.find_dates(line, strict=True)
    ]


month_year_re = re.compile(r'^(January|Jan|February|Feb|March|Mar|April|Apr|May|June|Jun|July|Jul|August|Aug|September|Sep|October|Oct|November|Nov|December|Dec) (1[89]\d\d)$')
year_re = re.compile(r'^1[89]\d\d$')

def match_full_line_date(text: str) -> list[str] | None:
    """Match a year or month year alone on a line of text."""
    dates = []
    for line in text.split('\n'):
        line = line.replace('.', '').strip()
        m = month_year_re.match(line)
        if m:
            dt = next(datefinder.find_dates(line))
            dates.append(dt.strftime('%Y-%m'))
            continue
        m = year_re.match(line)
        if m:
            dates.append(line)
    return dates


leadin_re = re.compile(r'(?:about|prior to|circa|c\.|views?.{0,6}:) (1[89]\d\d)')

def match_year_with_lead_in(text: str) -> list[str] | None:
    """Match 'about 1910' or 'prior to 1919'."""
    return [
        m.group(1)
        for m in re.finditer(r'(?:about|prior to) (1[89]\d\d)', text, re.I)
    ]


def get_dates_from_text(text: str):
    full_dates = match_full_date(text)
    full_lines = match_full_line_date(text)
    if full_dates or full_lines:
        # TODO: return order could match order in the text
        return full_lines + full_dates

    return match_year_with_lead_in(text)

