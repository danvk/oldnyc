#!/usr/bin/env python
'''Print out photo URLs with very early or very late dates.

Very early is pre-1860.
Very late is post-1945.

See https://github.com/danvk/oldnyc/issues/3
'''

import os, sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir) 
import re

import record

def extract_dates(date_str):
    return re.findall(r'\b(1[6789]\d\d)\b', date_str)


def mkurl(r):
    return 'http://digitalcollections.nypl.org/items/image_id/%s' % (
            re.sub(r'-[a-z]$', '', r.photo_id()))


if __name__ == '__main__':
    rs = record.AllRecords('nyc/records.pickle')
    for r in rs:
        dstr = re.sub(r'\s+', ' ', r.date())
        if not dstr: continue
        for d in extract_dates(dstr):
            if d < '1860' or d > '1945':
                print '%4s\t%s\t%s' % (d, r.photo_id(), mkurl(r))
