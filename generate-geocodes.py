#!/usr/bin/env python
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

# Import order here determines the order in which coders get a crack at each
# record. We want to go in order from precise to imprecise.
import coders.extended_grid
import coders.milstein
import coders.nyc_parks


if __name__ == '__main__':
  parser = OptionParser()
  parser.add_option('', '--pickle_path', default=None, dest='pickle_path',
                    help='Point to an alternative records.pickle file.')
  parser.add_option('', '--ids_filter', default='', dest='ids_filter',
                    help='Comma-separated list of Photo IDs to consider.')
  parser.add_option('', '--previous_geocode_json', default='',
                    dest='previous_geocode_json',
                    help='Path to a JSON file containing existing geocodes, ' +
                    'as output by this script with --output_format=records.js')

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
                    help='Set to either lat-lons.js, lat-lons-ny.js, records.js'
                    ' or entries.txt to output one of these formats.')
  parser.add_option('', '--lat_lon_map', default='', dest='lat_lon_map',
                    help='Lat/lon cluster map, built by cluster-locations.py. '
                    'Only used when outputting lat-lons.js')

  (options, args) = parser.parse_args()

  if options.geocode:
    g = geocoder.Geocoder(options.use_network, 2)  # 2s between geocodes
  else:
    g = None

  geocoders = coders.registration.coderClasses()
  geocoders = [coder() for coder in geocoders]

  if options.ok_coders != 'all':
    ok_coders = options.ok_coders.split(',')
    geocoders = [c for c in geocoders if c.name() in ok_coders]
    if len(geocoders) != len(ok_coders):
      sys.stderr.write('Coder mismatch: %s vs %s\n' % (options.ok_coders, ','.join([c.name() for c in geocoders])))
      sys.exit(1)

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

  # Load existing geocodes, if applicable.
  id_to_located_rec = {}
  if options.previous_geocode_json:
    prev_recs = json.load(file(options.previous_geocode_json))
    for rec in prev_recs:
      if 'extracted' in rec and 'latlon' in rec['extracted']:
        x = rec['extracted']
        id_to_located_rec[rec['id']] = (None, x['technique'], {
              'address': x['located_str'],
              'lat': x['latlon'][0],
              'lon': x['latlon'][1]
            })


  stats = defaultdict(int)
  located_recs = []  # array of (record, coder name, location_data) tuples
  for idx, r in enumerate(rs):
    if idx % 100 == 0 and idx > 0:
      sys.stderr.write('%5d / %5d records processed\n' % (1+idx, len(rs)))

    located_rec = (r, None, None)

    # Early-out if we've already successfully geocoded this record.
    if r.photo_id() in id_to_located_rec:
      rec = id_to_located_rec[r.photo_id()]
      located_rec = (r, rec[1], rec[2])
      located_recs.append(located_rec)
      stats[rec[1]] += 1
      continue

    # Give each coder a crack at the record, in turn.
    for c in geocoders:
      location_data = c.codeRecord(r)
      if not location_data: continue
      assert 'address' in location_data

      if not g:
        if options.print_recs:
          print('%s\t%s\t%s' % (
              c.name(), r.photo_id(), json.dumps(location_data)))
        stats[c.name()] += 1
        located_rec = (r, c.name(), location_data)
        break

      lat_lon = None
      try:
        geocode_result = g.Locate(location_data['address'])
        if geocode_result:
          lat_lon = c.getLatLonFromGeocode(geocode_result, location_data, r)
        else:
          sys.stderr.write('Failed to geocode %s\n' % r.photo_id())
          # sys.stderr.write('Location: %s\n' % location_data['address'])
      except Exception as e:
        sys.stderr.write('ERROR locating %s with %s\n' % (
            r.photo_id(), c.name()))
        #sys.stderr.write('ERROR location: "%s"\n' % json.dumps(location_data))
        raise

      if lat_lon:
        location_data['lat'] = lat_lon[0]
        location_data['lon'] = lat_lon[1]
        if options.print_recs:
          print('%s\t%f,%f\t%s\t%s' % (
              r.photo_id(), lat_lon[0], lat_lon[1], c.name(),
              json.dumps(location_data)))
        stats[c.name()] += 1
        located_rec = (r, c.name(), location_data)
        break

    located_recs.append(located_rec)

  # Let each geocoder know we're done. This is useful for printing debug info.
  for c in geocoders:
    c.finalize()

  successes = 0
  for c in geocoders:
    sys.stderr.write('%5d %s\n' % (stats[c.name()], c.name()))
    successes += stats[c.name()]

  sys.stderr.write('%5d (total)\n' % successes)

  if options.output_format == 'lat-lons.js':
    generate_js.printJson(located_recs, lat_lon_map)
  if options.output_format == 'lat-lons-ny.js':
    generate_js.printJsonNoYears(located_recs, lat_lon_map)
  elif options.output_format == 'records.js':
    generate_js.printRecordsJson(located_recs)
  elif options.output_format == 'entries.txt':
    generate_js.printRecordsText(located_recs)
  elif options.output_format == 'locations.txt':
    generate_js.printLocations(located_recs)
