import re


def extract_one_year(date_str):
    date_str = date_str.strip()
    if date_str == 'nd':
        return ''
    date_str = re.sub(r' [0-9][0-9]?[, ]', '', date_str)  # e.g. 'Jan 8,'
    date_str = re.sub(r'[^0-9]+', '', date_str)
    return date_str


def extract_years(date_str):
    return [
        extract_one_year(d)
        for d in re.split(r'[;-]', date_str)
    ]
