import re
from datetime import date

from dates import extract_years


def get_date_range(date_str: str) -> tuple[date, date] | None:
    # TODO: this is a bit wonky; could use clean_date more directly.
    years = extract_years(date_str)
    if not years or years == [""]:
        return date(1850, 1, 1), date(1999, 12, 31)
    dates = [date(int(y), 1, 1) for y in years]
    return min(dates), max(dates)


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
