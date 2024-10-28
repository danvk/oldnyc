# pyright: strict
import re

from .util import clean_date


def extract_years(date_str: str) -> list[str]:
    # return [extract_one_year(d) for d in re.split(r";|(?:-(?=\d{4}))", date_str)]
    date_str = re.sub(r"\[(\d{4})-(\d{4})\]", r"[\1, \2]", date_str)
    dates = clean_date(date_str).split(", ")
    years = [date[:4] for date in dates if re.match(r"^\d{4}", date)]
    return years or [""]
