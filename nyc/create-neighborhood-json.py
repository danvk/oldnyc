#!/usr/bin/python

import boroughs
import json
import shape_utils
import xml.etree.ElementTree as ET
tree = ET.parse('nyc-neighborhoods.xml')
root = tree.getroot()

neighborhood_to_coords = {}

for node in root:
  if node.tag == 'Placemark':
    neighborhood = node.findtext('.//name')
    coords = node.findtext('.//coordinates')
    xyzs = [[float(x) for x in y.split(',')] for y in coords.strip().split(' ')]
    lon_lats = [(xyz[0], xyz[1]) for xyz in xyzs]
    center_lon, center_lat, _ = shape_utils.CenterOfMass(lon_lats)
    boro = boroughs.PointToBorough(center_lat, center_lon)
    assert boro
    # Distinguish "Chelsea, Manhattan" from "Chelsea, Staten Island".
    neighborhood = '%s, %s' % (neighborhood, boro)
    neighborhood_to_coords[neighborhood] = lon_lats

json.dump(neighborhood_to_coords, file('neighborhood-polygons.json', 'w'))

