#!/usr/bin/env python
'''Clean up a few common warts in the OCR data from Ocropus.

These include:
    - \& --> &
    - '' --> "
    - Dropping "NO REPRODUCTIONS" lines
'''

import json
import re

import editdistance


def swap_chars(txt):
    return re.sub(r"''", '"', re.sub(r'\\&', '&', txt))


# See https://github.com/danvk/oldnyc/issues/39
WARNINGS = [
  'NO REPRODUCTIONS',
  'MAY BE REPRODUCED',
  'CREDIT LINE IMPERATIVE',
  'CREDIT LINE IMPERATIVE ON ALL REPRODUCTIONS'
]


def is_warning(line):
    line = re.sub(r'[,.]$', '', line)
    for base in WARNINGS:
        d = editdistance.eval(base, line)
        if 2 * d < len(base):
            return True
    return False


def remove_warnings(txt):
    return '\n'.join(line for line in txt.split('\n') if not is_warning(line))


def clean(txt):
    return remove_warnings(swap_chars(txt))


if __name__ == '__main__':
    ocr = json.load(open('ocr/ocr.json'))
    for k, txt in ocr.iteritems():
        clean(txt)
        #print '%s: %s' % (k, clean(txt))
