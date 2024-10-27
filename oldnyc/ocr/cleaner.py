#!/usr/bin/env python
r"""Clean up a few common warts in raw OCR output.

These include:
    - \& --> &
    - '' --> "
    - Dropping "NO REPRODUCTIONS" lines
    - Merging lines into paragraphs
"""

import json
import re

import editdistance

I_NUM_RE = re.compile(r"\bI(\d{3}|\d(?:st|nd|rd|th))", re.I)
II_NUM_RE = re.compile(r"\bII(\d(?:st|nd|rd|th))", re.I)


def swap_chars(txt: str) -> str:
    r"""Remove a few common Ocropusisms, like \& and ''"""
    txt = re.sub(r"\\&", "&", txt)
    txt = re.sub(r"''", '"', txt)
    txt = re.sub(I_NUM_RE, r"1\1", txt)
    txt = re.sub(II_NUM_RE, r"11\1", txt)
    txt = txt.replace("IIth", "11th")
    return txt


# See https://github.com/danvk/oldnyc/issues/39
WARNINGS = [
    "NO REPRODUCTIONS",
    "MAY BE REPRODUCED",
    "CREDIT LINE IMPERATIVE",
    "CREDIT LINE IMPERATIVE ON ALL REPRODUCTIONS",
]
WARNING_RE_STR = "|".join(WARNINGS)


YEAR_PAT = re.compile(r"\d{4}")


def is_warning(line: str):
    line = re.sub(r"[,.]$", "", line)
    # line = line.upper()
    for base in WARNINGS:
        d = editdistance.eval(base, line)
        # allow some wiggle room, but don't swallow anything that might be a date
        if 2 * d < len(base) and not re.search(YEAR_PAT, line):
            return True
    if re.match(r"President Borough of Manhatt[ae]n\.?", line):
        return True
    return False


def remove_warnings(txt: str) -> str:
    """Remove lines like "NO REPRODUCTIONS"."""
    # remove full warning lines
    txt = "\n".join(line for line in txt.split("\n") if not is_warning(line))
    # remove warnings at the end of lines
    lines = txt.split("\n")
    for i, line in enumerate(lines):
        for warning in WARNINGS:
            word = warning.split(" ")[0] + " "
            if word in line:
                idx = line.index(word)
                # allow some wiggle room, but don't swallow anything that might be a date
                d = editdistance.eval(warning, line[idx:])
                if 2 * d < len(warning) and not re.search(YEAR_PAT, line[idx:]):
                    lines[i] = line[: idx - 1]
    txt = "\n".join(lines)
    # As a final pass, remove all exact matches, wherever they occur
    # These are likely with LLMs, which tend to fix typos.
    txt = re.sub(r"(%s)\.?" % WARNING_RE_STR, "", txt, flags=re.IGNORECASE)
    return txt


def merge_lines(txt: str) -> str:
    """Merge sequential lines in a paragraph into a single line.

    This can't be done reliably from just the OCR'd text -- it would be better
    to do this using the bounding boxes of the original images -- but the
    monospaced font allows a reasonable approximation. Merging these lines is
    essential for letting the browser reflow the text, especially on narrower
    screens.
    """
    if not txt:
        return txt
    has_trailing_newline = txt[-1] == "\n"
    lines = txt.split("\n")
    width = max(len(line) for line in lines)
    join_width = width - 15
    if join_width < 25:
        return txt  # be conservative

    txt = ""
    for i, line in enumerate(lines):
        if line.endswith("-"):
            # A hyphen at end of line is an automatic join.
            txt += line[:-1]
            continue

        txt += line
        if len(line) < join_width:
            txt += "\n"
        elif i < len(lines) - 1 and len(lines[i + 1]) < join_width:
            txt += "\n"
        else:
            txt += " "
    if txt.endswith("\n\n"):
        txt = txt[:-1]
    if txt[-1] == "\n" and not has_trailing_newline:
        txt = txt[:-1]
    return txt


def is_negative(txt: str) -> bool:
    """Is this a negative / slide number?"""
    m = re.match(
        r"(?:neg(?:ative)?|slide)[. #;:]*(?:no\.? )?((?:[-A-Z #;.:_]*)\d+(?:[-A-Z #;.:_0-9]*))\.?$",
        txt,
        flags=re.I,
    )
    if m is None:
        return False
    neg_id = m.group(1)
    if "available" in neg_id:
        return True
    # Make sure there's not too many lower-case letters
    n_lower = 0
    for c in neg_id:
        if c.islower():
            n_lower += 1
    return n_lower < 10


def remove_neg(txt: str) -> str:
    """Remove text like "NEG #3039", "Slide #123", etc."""
    return "\n".join(line for line in txt.split("\n") if not is_negative(line))


def split_interior_whitespace(txt: str) -> str:
    """Sometimes GPT models two-column text with interior whitespace.

    We prefer distinct lines. This also normalizees leading/trailing whitespace and
    splits up (1), (2), (3), etc. that are all on the same line.
    """
    txt = re.sub(r" {10,}", "\n", txt)
    txt = "\n".join(line.strip() for line in txt.split("\n"))
    if txt.strip().count("\n") == 0 and " (2)" in txt:
        # False positives: 715300b and 715979b
        txt = re.sub(r" +(\(\d\))", r"\n\n\1", txt)
    return txt


def remove_stamps(txt: str) -> str:
    """Remove low-value text coming from stamps."""
    if re.search(r"F\. S\. Lincoln", txt, flags=re.I) or "THE NEW YORK PUBLIC LIBRARY" in txt:
        lines = txt.split("\n")
        recording = True
        out = []
        for line in lines:
            if line.lower() == "copyright by":
                continue
            if line.lower() == "f. s. lincoln" or line == "THE NEW YORK PUBLIC LIBRARY":
                recording = False
            elif not recording:
                if not line or line == "Photographer" or line.startswith("114"):
                    pass
                elif not re.match(r"^[-A-Z .,&/0-9]+$", line):
                    recording = True
            if recording:
                out.append(line)
        txt = "\n".join(out)
    return txt


def clean(txt: str):
    txt = swap_chars(txt)
    txt = split_interior_whitespace(txt)
    txt = remove_stamps(txt)
    txt = remove_neg(txt)
    txt = remove_warnings(txt)
    txt = merge_lines(txt)
    return txt


if __name__ == "__main__":
    ocr = json.load(open("data/gpt-ocr.json"))
    n = 0
    for k, r in ocr.items():
        txt = clean(r["text"])
        # if txt and txt.strip().count("\n") == 0 and " (2)" in txt:
        if " (2)" in txt:
            print(n, k, txt)
            n += 1
        # print '%s:\n%s\n\n-----\n' % (k, clean(txt))
        # txt = clean(txt)
        # txt = '\n'.join('%2d %s' % (len(line), line) for line in txt.split('\n'))
        # print '%s:\n%s\n\n------\n' % (k, txt)
