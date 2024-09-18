import re
from datetime import datetime


def normalize_whitespace(text: str) -> str:
    s = re.compile(r"\s+")
    return " ".join([x for x in s.split(text) if x])


def clean_title(title: str) -> str:
    if title.startswith("[") and title.endswith("]"):
        title = title[1:-1]
    title = title.rstrip(".")
    title = title.replace(" and , to", ", to")
    return title


def clean_date(date_str: str) -> str:
    date_str = date_str.strip()
    # Handle empty or unknown dates
    date_str = date_str.replace("n.d", "").replace("[Unknown]", "")
    if not date_str:
        return date_str

    # Remove brackets and "ca." prefix
    date_str = re.sub(r"\[ca\.?\s*|\[|\]", "", date_str)

    # Handle uncertain dates
    date_str = re.sub(r"\?", "", date_str)

    # Fix typos
    date_str = date_str.replace("Febraury", "February").replace("Janurary", "January")

    cleaned_dates = []
    for fmt in ("%Y, %B %d", "%Y, %b. %d", "%B %d, %Y", "%b. %d, %Y"):
        try:
            parsed_date = datetime.strptime(date_str, fmt)
            cleaned_dates.append(parsed_date.strftime("%Y-%m-%d"))
            date_str = ""
            break
        except ValueError:
            continue

    # Split multiple dates separated by semicolons or commas
    dates = re.split(r"[;,]", date_str)

    for date in dates:
        date = date.strip()
        # Try to parse the date in different formats
        for fmt in (
            "%Y",
            "%B %Y",
            "%b %Y",
            "%b. %Y",
            "%d %B %Y",
            "%d%B %Y",
            "%d %b %Y",
            "%d %B",
            "%d %b",
        ):
            try:
                parsed_date = datetime.strptime(date, fmt)
                if "%d" in fmt:
                    cleaned_dates.append(parsed_date.strftime("%Y-%m-%d"))
                elif "%B" in fmt or "%b" in fmt:
                    cleaned_dates.append(parsed_date.strftime("%Y-%m"))
                else:
                    cleaned_dates.append(parsed_date.strftime("%Y"))
                break
            except ValueError:
                continue
        else:
            # If no format matched, just add the cleaned date as is
            cleaned_dates.append(date)

    # Remove duplicates and sort the dates
    cleaned_dates = sorted({d for d in cleaned_dates if d})

    return ", ".join(cleaned_dates)


def clean_creator(creator: str) -> str:
    creator = creator.split("\n", 1)[0]
    return "; ".join(
        re.sub(r",\d{4}-\d{4}", "", re.sub(r"--Photographer.*", "", c)).strip()
        for c in creator.split(";")
    )


BOROUGHS = ("Manhattan", "Queens", "Brooklyn", "Bronx", "Staten Island")


STATES = {
    "Alabama",
    "Alaska",
    "Arizona",
    "Arkansas",
    "California",
    "Colorado",
    "Connecticut",
    "Delaware",
    "District of Columbia",
    "Florida",
    "Georgia",
    "Hawaii",
    "Idaho",
    "Illinois",
    "Indiana",
    "Iowa",
    "Kansas",
    "Kentucky",
    "Louisiana",
    "Maine",
    "Maryland",
    "Massachusetts",
    "Michigan",
    "Minnesota",
    "Mississippi",
    "Missouri",
    "Montana",
    "Nebraska",
    "Nevada",
    "New Hampshire",
    "New Jersey",
    "New Mexico",
    "New York",
    "North Carolina",
    "North Dakota",
    "Ohio",
    "Oklahoma",
    "Oregon",
    "Pennsylvania",
    "Rhode Island",
    "South Carolina",
    "South Dakota",
    "Tennessee",
    "Texas",
    "Utah",
    "Vermont",
    "Virginia",
    "Washington",
    "West Virginia",
    "Wisconsin",
    "Wyoming",
}
