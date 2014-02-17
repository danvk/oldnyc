#!/usr/bin/python
#
# Look for well-known NYC parks.

parks = {
  'Bronx: Bronx Park': (40.856389, -73.876667),
  'Bronx: Claremont Park': (40.840546, -73.907469),
  'Bronx: Crotona Park': (40.8388, -73.8952),
  'Bronx: Fulton Park': None,
  'Bronx: Morris Park Race Track': (40.85, -73.855556),
  'Bronx: Poe Park': (40.865278, -73.894444),
  'Bronx: Pulaski Park': (40.805239, -73.924409),
  'Bronx: Starlight Park': (40.834176, -73.881968),
  'Brooklyn: Highland Park': (40.688370, -73.887480),
  'Brooklyn: Marine Park': (40.59804, -73.92083),
  'Brooklyn: Prospect Park Plaza': (40.6743, -73.9702),
  'Brooklyn: Prospect Park': (40.66143, -73.97035),  # BIG!
  'Manhattan: Battery Park': (40.703717, -74.016094),
  'Manhattan: Bryant Park': (40.753792, -73.983607),
  'Manhattan: Central Park': (40.782865, -73.965355),  # BIG!
  'Manhattan: Colonial Park': (40.824293, -73.942172),
  'Manhattan: Cooper Park': (40.716014, -73.937268),
  'Manhattan: Jefferson Park': (40.793366, -73.935247),
  'Manhattan: Morningside Park': (40.805093, -73.959127),
  'Manhattan: Riverside Park': (40.801234, -73.972310),
  'Queens: Astoria Park': (40.775934, -73.925275),
  'Queens: Baisley Park': (40.677778, -73.784722),
  'Queens: Chisholm Park': (40.792833, -73.851857),
  'Queens: Rainey Park': (40.766070, -73.940758),
  'Richmond: Barrett Park': (40.6251, -74.1157)
}

islands = {
  'Barren Island': (40.592778, -73.893056),
  'Bedloe\'s Island': (40.690050, -74.045068),
  'City Island': (40.846820, -73.787498),
  'Coney Island beach': (40.572130, -73.979330),
  'Coney Island pier': (40.571413, -73.983822),
  'Coney Island': (40.574926, -73.985941),
  'Ellis Island': (40.699472, -74.039560),
  'Governor\'s Island': (40.689450, -74.016792),
  'Governors Island': (40.689450, -74.016792),
  'Hart\'s Island': (40.853627, -73.770585),
  'High Island': (40.859525, -73.785639),
  'Hoffman Island': (40.578873, -74.053688),
  'Hunter Island': (40.875028, -73.790219),
  'North Brother Island': (40.800720, -73.898137),
  'North Brothers Island': (40.800720, -73.898137),
  'Plumb Island': (40.584722, -73.915000),
  'Randall\'s Island': (40.793227, -73.921286),
  'Randalls Island': (40.793227, -73.921286),
  'Rikers Island': (40.793128, -73.886010),
  'Shooters Island': (40.643333, -74.159722),
  'South Brother Island': (40.796402, -73.898137),
  'Ward\'s Island': (40.793227, -73.921286),
  'Welfare Island': (40.762161, -73.949964)
}


# For fast iteration
if __name__ == '__main__':
  coder = NycParkCoder()
  r = record.Record()
  num_ok, num_bad = 0, 0
  for line in fileinput.input():
    addr = line.strip()
    if not addr: continue
    r.tabular = {
      'i': ['PHOTO_ID'],
      'l': [addr],
      'a': ['Milstein Division']
    }
    result = coder.codeRecord(r)

    print '"%s" -> %s' % (addr, result)
    if result:
      num_ok += 1
    else:
      num_bad += 1

  sys.stderr.write('Parsed %d / %d = %.4f records\n' % (
    num_ok, num_ok + num_bad, 1. * num_ok / (num_ok + num_bad)))
