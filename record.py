import re
import time
from datetime import date, timedelta

from typing import Optional, TypedDict


class Record(TypedDict):
    """Type of entries in records.json"""

    id: str
    location: str
    date: str
    description: Optional[str]
    title: str
    alt_title: str
    photo_url: str
    preferred_url: str
    back_id: Optional[str]
    borough: Optional[str]
    outside_nyc: bool


def extract_regex(pat: re.Pattern, str: str):
    """Return the first captured string of the regex or None if there was no match."""
    m = re.search(pat, str, re.DOTALL)
    if not m:
        return None
    try:
        return m.group(1)
    except IndexError:
        return None


def parse_month(mon):
    """Takes "Jan" -> 1"""
    return int(time.strptime(mon[0:3], "%b")[1])


# XXX November is misspelled
def abbreviate_months(txt):
    return (
        txt.replace("January", "Jan")
        .replace("February", "Feb")
        .replace("March", "Mar")
        .replace("April", "Apr")
        .replace("June", "Jun")
        .replace("July", "Jul")
        .replace("August", "Aug")
        .replace("September", "Sep")
        .replace("October", "Oct")
        .replace("Novemeber", "Nov")
        .replace("December", "Dec")
        .replace("Sept", "Sep")
    )


def get_date_range(r: Record) -> tuple[date, date] | None:
    p = extract_date_range(r["date"]) or [None, None]
    if p[0] is None:
        p[0] = date(1850, 1, 1)
    if p[1] is None:
        p[1] = date(1999, 12, 31)
    return p


def extract_date_range(raw_txt: str):
    """Return a [first, last] pair of datetime.date's from a string.
    Returns None if the date couldn't be parsed or [None, None] if the photo
    is undateable (e.g. the date is 'n.d.')."""

    txt = re.sub(r"[\[\].]", "", raw_txt).strip()  # strip '[', ']' and '.'
    # Undateable, e.g. "[n.d.]"
    if txt == "nd":
        return [None, None]

    # Just a year, e.g. "1928."
    year = extract_regex(r"^(\d{4})$", txt)
    if year:
        start = date(int(year), 1, 1)
        end = date(int(year), 12, 31)
        return [start, end]

    # A "circa" year, e.g. "[ca. 1915]"
    ca_year = extract_regex(r"^ca? ?(\d{4})$", txt)
    if ca_year:
        y = int(ca_year)
        start = date(y - 1, 1, 1)
        end = date(y + 1, 12, 31)
        return [start, end]

    # An uncertain year, e.g. "[1856?]"
    ca_year = extract_regex(r"^(\d{4})\?$", txt)
    if ca_year:
        y = int(ca_year)
        start = date(y - 1, 1, 1)
        end = date(y + 1, 12, 31)
        return [start, end]

    txt = abbreviate_months(txt)

    # An exact date with a 3-letter month abbrev., e.g. "1950 Aug. 25."
    m = re.match(r"^(\d{4}) ([A-Z][a-z]{2,3}) ?(\d{1,2})$", txt)
    if m:
        year, mon, day = m.groups()
        year, mon, day = int(year), parse_month(mon), int(day)

        # hacks to correct non-existent dates
        # I should notify the library of these.
        if mon == 4 and day == 31:
            mon, day = 5, 1
        if year == 1949 and mon == 2 and day == 29:
            mon, day = 3, 1
        if mon == 6 and day == 31:
            mon, day = 7, 1
        if mon == 2 and day == 31:
            mon, day = 3, 1
        if mon == 11 and day == 31:
            mon, day = 12, 1

        start = date(year, mon, day)
        return [start, start]

    # An exact date range, e.g. "1950 Aug. 25-27."
    m = re.match(r"^(\d{4}) ([A-Z][a-z]{2,3}) ?(\d{1,2})-(\d{1,2})$", txt)
    if m:
        year, mon, day1, day2 = m.groups()
        year, mon, day1, day2 = int(year), parse_month(mon), int(day1), int(day2)

        start = date(year, mon, day1)
        end = date(year, mon, day2)
        return [start, end]

    # A month and year, e.g. "1971 Aug."
    m = re.match(r"^(\d{4}) ([A-Z][a-z]{2,3})$", txt)
    if m:
        year, mon = m.groups()
        year, mon = int(year), parse_month(mon)
        start = date(year, mon, 1)
        # This monstrosity determines the last day of the month
        end = (start + timedelta(days=+32)).replace(day=1) + timedelta(days=-1)
        return [start, end]

    # A month and year, e.g. "Aug. 1971"
    m = re.match(r"^([A-Z][a-z]{2,3}) (\d{4})$", txt)
    if m:
        mon, year = m.groups()
        year, mon = int(year), parse_month(mon)
        start = date(year, mon, 1)
        # This monstrosity determines the last day of the month
        end = (start + timedelta(days=+32)).replace(day=1) + timedelta(days=-1)
        return [start, end]

    # A decade, e.g. "[194-]"
    dec = extract_regex(r"^([12]\d\d)-$", txt)
    if dec:
        year = int(dec + "0")
        start = date(year, 1, 1)
        end = date(year + 9, 12, 31)
        return [start, end]

    # Special case: "-1906"
    if txt == "-1906":
        return [date(1850, 1, 1), date(1906, 4, 17)]

    # A year range, e.g "1925-1928" or "1925-28"
    yr = re.search(r"^(\d{4}) *- *(\d{2,4})$", txt)
    if yr:
        start = int(yr.group(1))
        end = int(yr.group(2))
        if end < 100:
            end += 100 * int(start / 100)
        return [date(start, 1, 1), date(end, 12, 31)]

    # A pair of years, e.g. "1925 or 1926"
    yp = re.search(r"^(\d{4}) or (\d{4})$", txt)
    if yp:
        start = int(yp.group(1))
        end = int(yp.group(2))
        return [date(start, 1, 1), date(end, 12, 31)]

    # A pair of dates, e.g "[between (date1) and (date2)]"
    bt = re.search(r"^between (.*) and (.*)$", txt, re.IGNORECASE)
    if bt:
        left = Record.ExtractDateRange(bt.group(1))
        right = Record.ExtractDateRange(bt.group(2))
        if left and right:
            return [left[0], right[1]]

    # A century, e.g. "[19--]"
    # TODO(danvk): maybe throw these out? '19--' isn't very informative.
    cen = extract_regex(r"^([12]\d)--$", txt)
    if cen:
        year = int(cen + "00")
        start = date(year, 1, 1)
        end = date(year + 99, 12, 31)
        if cen == "18":
            start = date(1850, 1, 1)  # Photography isn't that old.
        return [start, end]

    # If there's a '?' or 'ca' then try it again, but ignore any uncertainty
    if "?" in txt or "ca" in txt:
        return extract_date_range(txt.replace("?", "").replace("ca", ""))

    return None


def clean_title(title: str) -> str:
    """remove [graphic] from titles"""
    title = title.replace(" [graphic].", "")
    title = title.replace("[", "").replace("]", "")
    return title


def clean_date(date: str) -> str:
    """remove [] and trailing period from dates"""
    if not date:
        return ""
    date = date.replace("[", "").replace("]", "").replace("\n", " ")
    if date[-1] == ".":
        date = date[:-1]
    return date


def clean_folder(folder: str) -> str:
    # remove leading 'Folder: ', trailing period & convert various forms of
    # dashes to a single form of slashes.
    if not folder:
        return ""
    if folder[-1] == "." and not folder[-3] == ".":  # e.g. 'Y.M.C.A'
        folder = folder[:-1]
    folder = folder.replace("Folder: ", "")
    folder = re.sub(r" *- *", " / ", folder)
    return folder
