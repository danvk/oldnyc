import re
from data.util import clean_date

def extract_one_year(date_str):
    date_str = date_str.strip()
    if date_str == 'nd':
        return ''
    date_str = re.sub(r' [0-9][0-9]?[, ]', '', date_str)  # e.g. 'Jan 8,'
    date_str = re.sub(r'[^0-9]+', '', date_str)
    return date_str


def extract_years(date_str):
    # return [extract_one_year(d) for d in re.split(r";|(?:-(?=\d{4}))", date_str)]
    date_str = re.sub(r"\[(\d{4})-(\d{4})\]", r"[\1, \2]", date_str)
    dates = clean_date(date_str).split(", ")
    years = [date[:4] for date in dates if re.match(r"^\d{4}", date)]
    return years or [""]
