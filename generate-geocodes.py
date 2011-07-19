#!/usr/bin/python
#
# This is the main driver for the geocoding process.
# Inputs are the records pickle and a collection of 'coders'.
# Output depends on command-line flags, but can be:
# o JSON for loading on the sf-viewer site.
# o XML for all records, including geocodable strings and lat/lons.

import sys
from collections import defaultdict
from optparse import OptionParser
import coders.registration
import coders.locatable
import record
import geocoder
import generate_js

# Import order here determines the order in which coders get a crack at each
# record. We want to go in order from precise to imprecise.
import coders.sf_residences
import coders.sf_streets
import coders.free_streets
import coders.catcodes
import coders.generalizations


if __name__ == '__main__':
  parser = OptionParser()
  parser.add_option("-c", "--coders", dest="ok_coders", default='all',
                    help="Set to a comma-separated list of coders")
  parser.add_option("-m", "--maps_key", dest="maps_key",
                    default=None, help="Your google maps API key.")
  parser.add_option("-g", "--geocode", dest="geocode", action="store_true",
                    default=False,
                    help="Set to geocode all locations. If set w/o " +
                    "--maps_key, will only use the geocache.")
  parser.add_option("-p", "--print_records", dest="print_recs",
                    action="store_true", default=False,
                    help="Set to print out records as they're coded.")
  parser.add_option("-o", "--output_format", default="",
                    help="Set to either lat-lons.js or records.xml to output " +
                    "one of these formats.")
  (options, args) = parser.parse_args()

  if options.geocode:
    g = geocoder.Geocoder(options.maps_key, 5)
  else:
    g = None

  coders = coders.registration.coderClasses()
  coders = [coder() for coder in coders]

  if options.ok_coders != 'all':
    ok_coders = options.ok_coders.split(',')
    coders = [c for c in coders if c.name() in ok_coders]

  rs = record.AllRecords()
  stats = defaultdict(int)
  located_recs = []  # array of (record, coder name, locatable) tuples
  for r in rs:
    located_rec = (r, None, None)
    for c in coders:
      locatable = c.codeRecord(r)
      if not locatable: continue
      if not g:
        if options.print_recs:
          print '%s\t%s\t%s' % (c.name(), r.photo_id(), locatable)
        stats[c.name()] += 1
        located_rec = (r, c.name(), locatable)
        break

      lat_lon = locatable.getLatLon(g)
      if lat_lon:
        if options.print_recs:
          print '%s\t%f,%f\t%s\t%s' % (
              r.photo_id(), lat_lon[0], lat_lon[1], c.name(), locatable)
        stats[c.name()] += 1
        located_rec = (r, c.name(), locatable)
        break
    located_recs.append(located_rec)

  successes = 0
  for c in coders:
    sys.stderr.write('%5d %s\n' % (stats[c.name()], c.name()))
    successes += stats[c.name()]
  sys.stderr.write('%5d (total)\n' % successes)

  if options.output_format == 'lat-lons.js':
    generate_js.printJson(located_recs)
