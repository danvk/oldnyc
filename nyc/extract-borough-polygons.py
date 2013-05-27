#!/usr/bin/python
"""Extracts polygons for the five boroughs from a .shp file.

Prints a JSON map from borough name -> list of closed polygons, i.e.

  borough name -> [ [[lon1,lat1], [lon2,lat2], ...], [...] ]

Can be used to detect bad geocodes."""

import shapefile
import shape_utils
import sys
import json


def ExtractPlaces(places, name_field):
  """Returns a place name -> ShapeRecord dict for Places.shp."""
  ok_places = {
      'New York County': 'Manhattan',
      'Queens County': 'Queens',
      'Kings County': 'Brooklyn',
      'Bronx County': 'Bronx',
      'Richmond County': 'Staten Island'
  }
  ret = {}
  for i, rec in enumerate(places.shapeRecords()):
    name = rec.record[name_field]
    if name not in ok_places: continue
    
    real_name = ok_places[name]

    ret[real_name] = rec
  return ret


if __name__ == '__main__':
  assert len(sys.argv) == 2
  ny_county_places = shapefile.Reader(sys.argv[1])
  boroughs = ExtractPlaces(ny_county_places, 5)

  for k in sorted(boroughs.keys()):
    shape = boroughs[k].shape
    boroughs[k] = shape_utils.SplitIntoPolygons(shape)

  # Test each borough
  bkp = (-73.963455,40.719053)
  mp = (-73.976827,40.723652)
  bxp = (-73.793793,40.867457)
  sip = (-74.117203,40.600969)
  qp = (-73.76152,40.750427)

  m = boroughs['Manhattan']
  q = boroughs['Queens']
  bk = boroughs['Brooklyn']
  bx = boroughs['Bronx']
  si = boroughs['Staten Island']

  assert True == shape_utils.PointInPolygon(mp, m)
  assert False == shape_utils.PointInPolygon(mp, q)
  assert False == shape_utils.PointInPolygon(mp, bk)
  assert False == shape_utils.PointInPolygon(mp, bx)
  assert False == shape_utils.PointInPolygon(mp, si)

  assert False == shape_utils.PointInPolygon(qp, m)
  assert True  == shape_utils.PointInPolygon(qp, q)
  assert False == shape_utils.PointInPolygon(qp, bk)
  assert False == shape_utils.PointInPolygon(qp, bx)
  assert False == shape_utils.PointInPolygon(qp, si)

  assert False == shape_utils.PointInPolygon(bkp, m)
  assert False == shape_utils.PointInPolygon(bkp, q)
  assert True  == shape_utils.PointInPolygon(bkp, bk)
  assert False == shape_utils.PointInPolygon(bkp, bx)
  assert False == shape_utils.PointInPolygon(bkp, si)

  assert False == shape_utils.PointInPolygon(bxp, m)
  assert False == shape_utils.PointInPolygon(bxp, q)
  assert False == shape_utils.PointInPolygon(bxp, bk)
  assert True  == shape_utils.PointInPolygon(bxp, bx)
  assert False == shape_utils.PointInPolygon(bxp, si)

  assert False == shape_utils.PointInPolygon(sip, m)
  assert False == shape_utils.PointInPolygon(sip, q)
  assert False == shape_utils.PointInPolygon(sip, bk)
  assert False == shape_utils.PointInPolygon(sip, bx)
  assert True == shape_utils.PointInPolygon(sip, si)

  print json.dumps(boroughs)
