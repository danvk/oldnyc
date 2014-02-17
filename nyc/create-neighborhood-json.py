#!/usr/bin/python

import boroughs
import json
import re
import shape_utils
import sys
import xml.etree.ElementTree as ET

def ReadKmlFile(path):
  neighborhood_to_coords = {}
  xmlstring = file(path).read()
  xmlstring = re.sub(r" xmlns='[^']+'", '', xmlstring, count=1)
  root = ET.fromstring(xmlstring)

  for node in root.findall('.//Placemark'):
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

  return neighborhood_to_coords


okc = ReadKmlFile('nyc-neighborhoods.xml')
custom = ReadKmlFile('extra-neighborhoods.kml')

overlap = set(okc.keys()).intersection(set(custom.keys()))
assert len(overlap) == 0

neighborhood_to_coords = {}
neighborhood_to_coords.update(okc)
neighborhood_to_coords.update(custom)

sys.stderr.write(
    'Loaded %d neighborhood polygons.\n' % len(neighborhood_to_coords))

json.dump(neighborhood_to_coords, file('neighborhood-polygons.json', 'w'))

