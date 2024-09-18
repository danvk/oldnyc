import re


def clean_title(title: str) -> str:
    # strip [] from [delimited] sections at the end
    title = re.sub(r"\[(.*?)\]$", r"\1", title)
    title = title.rstrip(".")
    title = title.replace(" and , to", ", to")
    return title
