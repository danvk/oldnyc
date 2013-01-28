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
import cPickle
import coders.cached_coder

# Import order here determines the order in which coders get a crack at each
# record. We want to go in order from precise to imprecise.
import coders.milstein
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
                    help="Set to either lat-lons.js, records.js or entries.txt "
                    "to output one of these formats.")
  parser.add_option("", "--from_cache", default="", dest="from_cache",
                    help="Set to a comma-separated list of coders to read " +
                    "them from the pickle cache instead of regenerating.")
  parser.add_option("", "--write_cache", default=False, dest="write_cache",
                    action="store_true", help="Create pickle cache")
  parser.add_option("", "--ids_filter", default="", dest="ids_filter",
                    help="Comma-separated list of Photo IDs to consider.")
  parser.add_option("", "--lat_lon_map", default="", dest="lat_lon_map",
                    help="Lat/lon cluster map, built by cluster-locations.py. "
                    "Only used when outputting lat-lons.js")
  parser.add_option("", "--pickle_path", default=None, dest="pickle_path",
                    help="Point to an alternative records.pickle file.")

  (options, args) = parser.parse_args()

  if options.geocode:
    g = geocoder.Geocoder(options.maps_key, 5)
  else:
    g = None

  geocoders = coders.registration.coderClasses()
  geocoders = [coder() for coder in geocoders]

  if options.ok_coders != 'all':
    ok_coders = options.ok_coders.split(',')
    geocoders = [c for c in geocoders if c.name() in ok_coders]

  cache_coders = options.from_cache.split(',')
  for idx, coder in enumerate(geocoders):
    if coder.name() in cache_coders:
      geocoders[idx] = coders.cached_coder.CachedCoder(coder.name())
  cache = defaultdict(list)

  lat_lon_map = {}
  if options.lat_lon_map:
    for line in file(options.lat_lon_map):
      line = line.strip()
      if not line: continue
      old, new = line.split('->')
      lat_lon_map[old] = new

  rs = record.AllRecords(path=options.pickle_path)
  if options.ids_filter:
    ids = set(options.ids_filter.split(','))
    rs = [r for r in rs if r.photo_id() in ids]

  stats = defaultdict(int)
  located_recs = []  # array of (record, coder name, locatable) tuples
  for r in rs:
    located_rec = (r, None, None)
    for c in geocoders:
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
    if options.write_cache and located_rec[1]:
      cache[located_rec[1]].append((r.photo_id(), located_rec[2]))


  successes = 0
  for c in geocoders:
    sys.stderr.write('%5d %s\n' % (stats[c.name()], c.name()))
    successes += stats[c.name()]
    if options.write_cache:
      output_file = "/tmp/coder.%s.pickle" % c.name()
      f = file(output_file, "w")
      p = cPickle.Pickler(f, 2)
      p.dump(cache[c.name()])

  sys.stderr.write('%5d (total)\n' % successes)

  if options.output_format == 'lat-lons.js':
    generate_js.printJson(located_recs, lat_lon_map)
  elif options.output_format == 'records.js':
    generate_js.printRecordsJson(located_recs)
  elif options.output_format == 'entries.txt':
    generate_js.printRecordsText(located_recs)
  elif options.output_format == 'locations.txt':
    generate_js.printLocations(located_recs)
