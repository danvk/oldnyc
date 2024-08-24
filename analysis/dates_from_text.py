"""Extract dates from backing text.

Sometimes there's a date in the text on the back of the card that's not in NYPL
metadata. We have to be careful to extract the date when the photo was taken, not
just some date mentioned in the photo.
"""

import re

import datefinder

by_full_date = 0
by_full_line = 0
by_leadin = 0

def parse_mon_year(mon_year: str):
    dt = next(datefinder.find_dates(mon_year))
    return dt.strftime('%Y-%m')


def match_full_date(text: str) -> list[str] | None:
    """Match any complete month day, year-style date."""
    return [
        date.strftime('%Y-%m-%d')
        for line in text.split('\n')
        for date in datefinder.find_dates(line, strict=True)
    ]


mon_pat = r'(?:January|Jan|February|Feb|March|Mar|April|Apr|May|June|Jun|July|Jul|August|Aug|September|Sep|October|Oct|November|Nov|December|Dec)'
year_pat = r'(?:1[89]\d\d)'
month_year_re = re.compile(r'^(%s) (%s)$' % (mon_pat, year_pat))
year_re = re.compile(r'^%s$' % year_pat)

def match_full_line_date(text: str) -> list[str] | None:
    """Match a year or month year alone on a line of text."""
    dates = []
    for line in text.split('\n'):
        line = line.replace('.', '').strip()
        m = month_year_re.match(line)
        if m:
            dates.append(parse_mon_year(line))
            continue
        m = year_re.match(line)
        if m:
            dates.append(line)
    return dates


leadin_pat = r'(?:about|prior to|circa|c\.|views?.{0,6}:)'
leadin_re = re.compile(r'%s (%s)' % (leadin_pat, year_pat), re.I)
leadin_mon_year_re = re.compile(r'%s ?(%s %s)' % (leadin_pat, mon_pat, year_pat), re.I)

def match_year_with_lead_in(text: str) -> list[str] | None:
    """Match 'about 1910' or 'prior to 1919'."""
    dates = []
    for m in re.finditer(leadin_mon_year_re, text):
        dates.append(parse_mon_year(m.group(1)))
    if dates:
        return dates
    return [
        m.group(1)
        for m in re.finditer(leadin_re, text)
    ]


def get_dates_from_text(text: str):
    global by_full_line, by_full_date, by_leadin
    full_dates = match_full_date(text)
    full_lines = match_full_line_date(text)
    if full_dates:
        by_full_date += 1
    elif full_lines:
        by_full_line += 1
    if full_dates or full_lines:
        # TODO: return order could match order in the text
        return full_lines + full_dates

    leadins = match_year_with_lead_in(text)
    if leadins:
        by_leadin += 1
    return leadins


def log_stats():
    print(f'{by_full_date=}, {by_full_line=}, {by_leadin=}')
