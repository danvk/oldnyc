#!/usr/bin/python
#
# This is the main driver for the geocoding process.
# Inputs are the records pickle and a collection of 'coders'.
# Output depends on command-line flags, but can be:
# o JSON for loading on the sf-viewer site.
# o XML for all records, including geocodable strings and lat/lons.

import coders.registration
import coders.locatable
import record

# Import order here determines the order in which coders get a crack at each
# record. We want to go in order from precise to imprecise.
import coders.sf_residences
import coders.sf_streets
import coders.free_streets
import coders.catcodes

coders = coders.registration.coderClasses()
coders = [coder() for coder in coders]

rs = record.AllRecords()
for r in rs:
  for c in coders:
    loc = c.codeRecord(r)
    if loc:
      print '%s: %s (folder=%s, title=%s)' % (
          c.name(), loc, r.location(), record.CleanTitle(r.title()))
      break
