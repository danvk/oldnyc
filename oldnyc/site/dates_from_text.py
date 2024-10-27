"""Extract dates from backing text.

Sometimes there's a date in the text on the back of the card that's not in NYPL
metadata. We have to be careful to extract the date when the photo was taken, not
just some date mentioned in the photo.
"""

import re
from datetime import datetime

import datefinder

by_full_date1 = 0
by_full_date2 = 0
by_full_line = 0
by_leadin = 0
by_inline_my = 0
by_inline_year = 0


def parse_mon_year(mon_year: str):
    mon_year = re.sub(r"sept\b", "sep", mon_year, flags=re.I)
    dt = next(datefinder.find_dates(mon_year))
    assert isinstance(dt, datetime)
    return dt.strftime("%Y-%m")


WEIRD_DATES = {
    "September 31, 1926": "1926-09-30",
    "April 31, 1930": "1930-04-30",
    "February 30, 1928": "1928-02-29",
    "November 31st, 1915": "1915-11-30",
    "November 311940": "1940-11-30",
    "November 31 1940": "1940-11-30",
    "September 31, 1935": "1935-09-30",
    "November 0, 1927": "1927-11-01",
}


def parse_mon_year_date(mon_year_date: str):
    mon_year_date = re.sub(r"sept\b", "sep", mon_year_date, flags=re.I)
    try:
        dt = next(datefinder.find_dates(mon_year_date))
    except StopIteration:
        patch = WEIRD_DATES.get(mon_year_date)
        if patch:
            return patch
        print(f"Failed to parse date: {mon_year_date=}")
        return
    assert isinstance(dt, datetime)
    return dt.strftime("%Y-%m-%d")


mon_pat = r"(?:January|Jan\.?|February|Feb\.?|March|Mar\.?|April|Apr\.?|May|June|Jun\.?|July|Jul\.?|August|Aug\.?|September|Sept?\.?|October|Oct\.?|November|Nov\.?|December|Dec\.?)"
year_pat = r"(?:1[89]\d\d)"
month_year_re = re.compile(r"^(%s),? (%s)$" % (mon_pat, year_pat))
floating_month_year_re = re.compile(r"\b(%s),? (%s)\b" % (mon_pat, year_pat), flags=re.I)
year_re = re.compile(r"^%s$" % year_pat)
anchored_year_re = re.compile(r"[ .] (%s)\." % year_pat)


def split_with_indices(txt: str, delim: str):
    indices: list[int] = []
    start = 0
    while True:
        try:
            idx = txt.index(delim, start)
        except ValueError:
            break
        indices.append(idx)
        start = idx + 1

    indices = [-1] + indices + [len(txt)]
    return [(txt[a + len(delim) : b], a + len(delim), b) for a, b in zip(indices, indices[1:])]


def match_full_line_date(text: str):
    """Match a year or month year alone on a line of text."""
    date_spans: list[tuple[str, int, int]] = []
    for raw_line, a, b in split_with_indices(text, "\n"):
        line = raw_line.replace(".", "").strip()
        m = month_year_re.match(line)
        if m:
            date_spans.append((parse_mon_year(line), a, b))
            continue
        m = year_re.match(line)
        if m:
            date_spans.append((line, a, b))
    return date_spans


full_date_re = re.compile(
    r"%s (?:\d|[12]\d|3[01])(?:(?:st|nd|rd|th)\.?)?[,.]? ?%s" % (mon_pat, year_pat), re.I
)


def match_full_date_re(text: str):
    """Sometimes datefinder misses a date."""
    date_spans: list[tuple[str, int, int]] = []
    for m in re.finditer(full_date_re, text):
        # print(f'{m.group(0)}')
        date = parse_mon_year_date(m.group(0))
        if date:
            date_spans.append((date, *m.span()))
    return date_spans


season_pat = r"winter|spring|summer|fall"
leadin_pat = r"(?:about|prior to|circa|c\.|views?.{0,6}:|(?:%s),?|(?:no\. \d:))" % season_pat
leadin_re = re.compile(r"%s (%s)" % (leadin_pat, year_pat), re.I)
leadin_mon_year_re = re.compile(r"%s ?(%s,? %s)" % (leadin_pat, mon_pat, year_pat), re.I)


def match_year_with_lead_in(text: str):
    """Match 'about 1910' or 'prior to 1919'."""
    date_spans: list[tuple[str, int, int]] = []
    for m in re.finditer(leadin_mon_year_re, text):
        date_spans.append((parse_mon_year(m.group(1)), *m.span()))
    for m in re.finditer(leadin_re, text):
        start, stop = m.span()
        bad = False
        for _, mstart, mstop in date_spans:
            if start >= mstart and stop <= mstop:
                bad = True
                break
        if not bad:
            date_spans.append((m.group(1), *m.span(1)))
    return date_spans


def get_inline_month_year(text: str):
    date_spans: list[tuple[str, int, int]] = []
    for m in re.finditer(floating_month_year_re, text):
        my = m.group(1) + " " + m.group(2)
        date_spans.append((parse_mon_year(my), *m.span()))
    return date_spans


def get_inline_year(text: str):
    date_spans: list[tuple[str, int, int]] = []
    for m in re.finditer(anchored_year_re, text):
        date_spans.append((m.group(1), *m.span(1)))
    return date_spans


def get_dates_from_text(text: str) -> list[str]:
    # TODO: replace with Counter()
    global by_full_line, by_full_date1, by_full_date2, by_leadin, by_inline_my, by_inline_year
    full_dates1 = []  # match_full_date_datefinder(text)
    full_dates2 = match_full_date_re(text)
    full_lines = match_full_line_date(text)
    if full_dates1:
        by_full_date1 += 1
    elif full_dates2:
        by_full_date2 += 1
    elif full_lines:
        by_full_line += 1

    leadins = match_year_with_lead_in(text)
    if leadins:
        by_leadin += 1
    inline_my = get_inline_month_year(text)
    if inline_my:
        by_inline_my += 1
    inline_year = get_inline_year(text)
    if inline_year:
        by_inline_year += 1

    date_spans = full_dates1 + full_dates2 + full_lines + leadins + inline_my + inline_year
    if not date_spans:
        return []

    date_spans.sort(key=lambda x: (x[1], -x[2]))
    uniq_spans = [date_spans[0]]
    for d, start, stop in date_spans[1:]:
        if start >= uniq_spans[-1][2]:
            uniq_spans.append((d, start, stop))
    return [ds[0] for ds in uniq_spans]


def log_stats():
    print(
        f"{by_full_date1=}, {by_full_date2=}, {by_full_line=}, {by_leadin=}, {by_inline_my=}, {by_inline_year=}"
    )
