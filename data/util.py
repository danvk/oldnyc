import re


def clean_title(title: str) -> str:
    # strip [] from [delimited] sections at the end
    title = re.sub(r"\[(.*?)\]$", r"\1", title)
    title = title.rstrip(".")
    title = title.replace(" and , to", ", to")
    return title


def clean_date(date_str):

    # Remove brackets and "ca." prefix
    date_str = re.sub(r"\[|\]|ca\. ?|Unknown", "", date_str)

    # Replace semicolons with commas
    date_str = date_str.replace(";", ",")

    # Remove "n.d" and "?"
    date_str = date_str.replace("n.d", "").replace("?", "")

    # Split the dates, sort them, and join them back
    dates = sorted(d.strip() for d in date_str.split(","))

    # Join the dates back with commas
    return ", ".join(date.strip() for date in dates if date.strip())
