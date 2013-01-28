#!/usr/bin/python
#
# Run whatever's in the "location" field directly through the geocoder.
# This almost never makes sense for SFPL records, but it does for the
# NYPL Milstein collection.

import coders.locatable
import coders.registration
import re


class MilsteinCoder:
  def __init__(self):
    pass

  def codeRecord(self, r):
    if r.source() != 'Milstein Division': return None

    # example: "100th Street (East) & 1st Avenue, Manhattan, NY"

    raw_loc = r.location().strip()
    loc = re.sub(r'^[ ?\t"\[]+|[ ?\t"\]]+$', '', raw_loc)
    if not loc: return None

    m = re.match(r'(.*) & (.*), ((?:Manhattan|Brooklyn|Bronx|Queens|Staten Island), NY)', loc)
    if not m: return None

    l = coders.locatable.fromCross(
        m.group(1), m.group(2), city=m.group(3), source=raw_loc)
    return l

  def name(self):
    return 'milstein'


coders.registration.registerCoderClass(MilsteinCoder)
