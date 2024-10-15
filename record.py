import re
import time
from datetime import date, timedelta

from dates import extract_years


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


def get_date_range(date_str: str) -> tuple[date, date] | None:
    years = extract_years(date_str)
    if not years or years == [""]:
        p = [None, None]
    else:
        dates = [date(int(y), 1, 1) for y in years]
        p = [min(dates), max(dates)]
    if p[0] is None:
        p[0] = date(1850, 1, 1)
    if p[1] is None:
        p[1] = date(1999, 12, 31)
    return p


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
