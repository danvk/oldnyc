#!/usr/bin/python
#
# Run whatever's in the "location" field directly through the geocoder.
# This almost never makes sense for SFPL records, but it does for the
# NYPL Milstein collection.

import coders.locatable
import coders.registration


class MilsteinCoder:
  def __init__(self):
    pass

  def codeRecord(self, r):
    if r.source() != 'Milstein Division': return None

    loc = r.location().strip()
    if not loc: return None

    return coders.locatable.fromInt(loc, source=loc)

  def name(self):
    return 'milstein spreadsheet'


coders.registration.registerCoderClass(MilsteinCoder)
