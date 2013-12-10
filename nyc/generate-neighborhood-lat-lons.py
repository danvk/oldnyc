#!/usr/bin/python
'''
Reads a lat-lons.js file (as output by generate-geocodes.py) and groups the
lat/lons by neighborhood.
'''

from collections import defaultdict
import sys
import boroughs
import json

# Remove the leading "var lat_lons = {" and trailing "};" from lat-lons.js to
# make it a true JSON file.
json_data = file(sys.argv[1]).read().replace('var lat_lons = ', '').replace('};', '}')

lat_lons = json.loads(json_data)

neighborhood_to_photos = defaultdict(list)
count = 0
for lat_lon, photos_list in lat_lons.iteritems():
  lat, lon = [float(x) for x in lat_lon.split(',')]
  neighborhood = boroughs.PointToNeighborhood(lat, lon)
  if not neighborhood:
    continue

  neighborhood_to_photos[neighborhood].extend(photos_list)

  count += 1
  if count % 2000 == 0:
    sys.stderr.write('%d...\n' % count)

for k, v in neighborhood_to_photos.iteritems():
  v.sort(key=lambda x: x[1])

# TODO(danvk): less precision in polygons to save space!
print 'var neighborhood_photos = %s;' % json.dumps(
    neighborhood_to_photos, separators=(',', ':'))
print
print 'var neighborhood_polygons = %s;' % file('neighborhood-polygons.json').read()
