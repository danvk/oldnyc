# pyright: strict
from datetime import date

from oldnyc.ingest.dates import extract_years


# TODO: move this into generate_js.py
def get_date_range(date_str: str) -> tuple[date, date]:
    # TODO: this is a bit wonky; could use clean_date more directly.
    years = extract_years(date_str)
    if not years or years == [""]:
        return date(1850, 1, 1), date(1999, 12, 31)
    dates = [date(int(y), 1, 1) for y in years]
    return min(dates), max(dates)
