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
import record
import geocoder
import generate_js
import json
import cPickle

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
  parser.add_option('', '--pickle_path', default=None, dest='pickle_path',
                    help='Point to an alternative records.pickle file.')
  parser.add_option('', '--ids_filter', default='', dest='ids_filter',
                    help='Comma-separated list of Photo IDs to consider.')

  parser.add_option('-c', '--coders', dest='ok_coders', default='all',
                    help='Set to a comma-separated list of coders')

  parser.add_option('-g', '--geocode', dest='geocode', action='store_true',
                    default=False,
                    help='Set to geocode all locations. The alternative is ' +
                    'to extract location strings but not geocode them. This ' +
                    'can be useful with --print_records.')
  parser.add_option('-n', '--use_network', dest='use_network',
                    action='store_true', default=False,
                    help='Set this to make the geocoder use the network. The ' +
                    'alternative is to use only the geocache.')

  parser.add_option('-p', '--print_records', dest='print_recs',
                    action='store_true', default=False,
                    help='Set to print out records as they\'re coded.')
  parser.add_option('-o', '--output_format', default='',
                    help='Set to either lat-lons.js, records.js or entries.txt '
                    'to output one of these formats.')
  parser.add_option('', '--lat_lon_map', default='', dest='lat_lon_map',
                    help='Lat/lon cluster map, built by cluster-locations.py. '
                    'Only used when outputting lat-lons.js')

  (options, args) = parser.parse_args()

  if options.geocode:
    g = geocoder.Geocoder(options.use_network, 5)
  else:
    g = None

  geocoders = coders.registration.coderClasses()
  geocoders = [coder() for coder in geocoders]

  if options.ok_coders != 'all':
    ok_coders = options.ok_coders.split(',')
    geocoders = [c for c in geocoders if c.name() in ok_coders]

  # TODO(danvk): does this belong here?
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
  located_recs = []  # array of (record, coder name, location_data) tuples
  for r in rs:
    located_rec = (r, None, None)
    for c in geocoders:
      location_data = c.codeRecord(r)
      if not location_data: continue
      assert 'address' in location_data

      if not g:
        if options.print_recs:
          print '%s\t%s\t%s' % (c.name(), r.photo_id(), json.dumps(location_data))
        stats[c.name()] += 1
        located_rec = (r, c.name(), location_data)
        break

      try:
        geocode_result = g.Locate(location_data['address'])
        lat_lon = c.getLatLonFromGeocode(geocode_result, location_data, r)
      except Exception as e:
        sys.stderr.write('ERROR locating %s with %s\n' % (
            json.dumps(location_data), c.name()))
        raise

      if lat_lon:
        location_data['lat'] = lat_lon[0]
        location_data['lon'] = lat_lon[1]
        if options.print_recs:
          print '%s\t%f,%f\t%s\t%s' % (
              r.photo_id(), lat_lon[0], lat_lon[1], c.name(),
              json.dumps(location_data))
        stats[c.name()] += 1
        located_rec = (r, c.name(), location_data)
        break

    located_recs.append(located_rec)


  successes = 0
  for c in geocoders:
    sys.stderr.write('%5d %s\n' % (stats[c.name()], c.name()))
    successes += stats[c.name()]

  sys.stderr.write('%5d (total)\n' % successes)

  if options.output_format == 'lat-lons.js':
    generate_js.printJson(located_recs, lat_lon_map)
  elif options.output_format == 'records.js':
    generate_js.printRecordsJson(located_recs)
  elif options.output_format == 'entries.txt':
    generate_js.printRecordsText(located_recs)
  elif options.output_format == 'locations.txt':
    generate_js.printLocations(located_recs)
