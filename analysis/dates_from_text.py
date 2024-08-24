"""Extract dates from backing text.

Sometimes there's a date in the text on the back of the card that's not in NYPL
metadata. We have to be careful to extract the date when the photo was taken, not
just some date mentioned in the photo.
"""

import re

import datefinder

by_full_date1 = 0
by_full_date2 = 0
by_full_line = 0
by_leadin = 0

def parse_mon_year(mon_year: str):
    mon_year = re.sub(r'sept\b', 'sep', mon_year, flags=re.I)
    dt = next(datefinder.find_dates(mon_year))
    return dt.strftime('%Y-%m')


def parse_mon_year_date(mon_year_date: str):
    mon_year_date = re.sub(r'sept\b', 'sep', mon_year_date, flags=re.I)
    try:
        dt = next(datefinder.find_dates(mon_year_date))
    except StopIteration:
        print(f'Failed to parse date: {mon_year_date=}')
        return
    return dt.strftime('%Y-%m-%d')


def match_full_date_datefinder(text: str) -> list[str] | None:
    """Match any complete month day, year-style date."""
    return [
        date.strftime('%Y-%m-%d')
        for line in text.split('\n')
        for date in datefinder.find_dates(line, strict=True)
    ]


mon_pat = r'(?:January|Jan.?|February|Feb.?|March|Mar.?|April|Apr.?|May|June|Jun.?|July|Jul.?|August|Aug.?|September|Sept?.?|October|Oct.?|November|Nov.?|December|Dec.?)'
year_pat = r'(?:1[89]\d\d)'
month_year_re = re.compile(r'^(%s),? (%s)$' % (mon_pat, year_pat))
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


full_date_re = re.compile(
    r'%s (?:\d|[12]\d|3[01]),? ?%s' % (mon_pat, year_pat), re.I
)

def match_full_date_re(text: str) -> list[str]:
    """Sometimes datefinder misses a date."""
    dates = []
    for m in re.finditer(full_date_re, text):
        # print(f'{m.group(0)}')
        date = parse_mon_year_date(m.group(0))
        if date:
            dates.append(date)
    return dates


season_pat = r'winter|spring|summer|fall'
leadin_pat = r'(?:about|prior to|circa|c\.|views?.{0,6}:|(?:%s),?|(?:no\. \d:))' % season_pat
leadin_re = re.compile(r'%s (%s)' % (leadin_pat, year_pat), re.I)
leadin_mon_year_re = re.compile(r'%s ?(%s,? %s)' % (leadin_pat, mon_pat, year_pat), re.I)

def match_year_with_lead_in(text: str) -> list[str]:
    """Match 'about 1910' or 'prior to 1919'."""
    dates = []
    spans = []
    for m in re.finditer(leadin_mon_year_re, text):
        dates.append(parse_mon_year(m.group(1)))
        spans.append(m.span())
    for m in re.finditer(leadin_re, text):
        start, stop = m.span()
        bad = False
        for span in spans:
            if start >= span[0] and stop <= span[1]:
                bad = True
                break
        if not bad:
            dates.append(m.group(1))
    return dates


def get_dates_from_text(text: str):
    global by_full_line, by_full_date1, by_full_date2, by_leadin
    full_dates1 = match_full_date_datefinder(text)
    full_dates2 = match_full_date_re(text)
    full_lines = match_full_line_date(text)
    if full_dates1:
        by_full_date1 += 1
    elif full_dates2:
        by_full_date2 += 1
    elif full_lines:
        by_full_line += 1
    if full_dates1 or full_dates2 or full_lines:
        # TODO: return order could match order in the text
        return full_lines + full_dates1 + [d for d in full_dates2 if d not in full_dates1]

    leadins = match_year_with_lead_in(text)
    if leadins:
        by_leadin += 1
    return leadins


def log_stats():
    print(f'{by_full_date1=}, {by_full_date2=}, {by_full_line=}, {by_leadin=}')
