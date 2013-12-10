import copy
import sys
import math

def SplitIntoPolygons(shape):
  """Returns a list of closed polygons."""
  ret = []
  this_polygon = []
  restart_indices = set(shape.parts)
  for idx, point in enumerate(shape.points):
    if idx in restart_indices:
      if this_polygon:
        ret.append(this_polygon)
      this_polygon = [[point[0], point[1]]]
    else:
      this_polygon.append([point[0], point[1]])
  if this_polygon:
    ret.append(this_polygon)
  return ret


def AreaOfPolygon(points):
  """Calculates the area of a (closed) polygon."""
  # Note: area will be negative for clockwise shapes.
  # See http://paulbourke.net/geometry/polyarea/
  A = 0
  N = len(points)
  for i in xrange(0, N):
    x_i = points[i][0]
    y_i = points[i][1]
    x_ip1 = points[(i+1) % N][0]
    y_ip1 = points[(i+1) % N][1]
    A += (x_i * y_ip1 - x_ip1 * y_i)
  return A / 2


def CenterOfMass(points):
  """Returns a (cx, cy, A) tuple."""
  A = AreaOfPolygon(points)
  N = len(points)
  cx = 0
  cy = 0
  for i in xrange(0, N):
    x_i = points[i][0]
    y_i = points[i][1]
    x_ip1 = points[(i+1) % N][0]
    y_ip1 = points[(i+1) % N][1]
    part = (x_i * y_ip1 - x_ip1 * y_i)
    cx += ((x_i + x_ip1) * part)
    cy += ((y_i + y_ip1) * part)
  return (cx/(6*A), cy/(6*A), abs(A))


def _dot(a, b):
  return a[0] * b[0] + a[1] * b[1]

def _norm(x):
  return math.sqrt(_dot(x, x))

def _norm2(x):
  return _dot(x, x)

def _minus(a, b):
  return (a[0] - b[0], a[1] - b[1])

def DistanceToPolygon(point, points):
  """Returns the distance from a point to the edge of a polygon."""
  minDist = float('inf')
  for p1, p2 in zip(points[:-1], points[1:]):
    p2_p1 = (p2[0] - p1[0], p2[1] - p1[1])
    x_p1 = (point[0] - p1[0], point[1] - p1[1])
    np2_p1 = _norm(p2_p1)
    if np2_p1 == 0:
      continue
    r = 1. * _dot(p2_p1, x_p1) / (np2_p1 ** 2)
    
    if r < 0:
      dist = _norm(x_p1)
    elif r > 1:
      dist = _norm( (p2[0] - point[0], p2[1] - point[1]) )
    else:
      n = (p2_p1[0] / np2_p1, p2_p1[1] / np2_p1)
      k = _dot(x_p1, n)
      n = (n[0] * k, n[1] * k)
      dist = _norm(_minus(x_p1, n))
      #dist = math.sqrt(_norm2(x_p1) - r * _norm2(p2_p1))
    minDist = min(dist, minDist)

  return minDist


def CenterOfMassForShape(shape):
  """Returns a (cx, cy) tuple for a set of polygons."""
  polygons = SplitIntoPolygons(shape)
  total_A = 0
  total_cx = 0
  total_cy = 0

  for polygon in polygons:
    cx, cy, A = CenterOfMass(polygon)
    total_cx += A * cx
    total_cy += A * cy
    total_A += A

  return (total_cx / total_A, total_cy / total_A)


def AreaForShape(shape):
  """Finds the area of a shape."""
  total_A = 0

  for polygon in SplitIntoPolygons(shape):
    cx, cy, A = CenterOfMass(polygon)
    total_A += A

  return total_A


def TranslateShape(shape, dx, dy):
  """Modifies a shape object's points array."""
  for i, point in enumerate(shape.points):
    shape.points[i] = [ point[0] + dx, point[1] + dy ]


def GetShapeBoundingBox(shape):
  """Returns a {x, y, w, h} dict. (x, y) is the NW corner."""
  x, y = shape.points[0]
  x_low, x_high = x, x
  y_low, y_high = y, y

  for x, y in shape.points[1:]:
    x_low = min(x, x_low)
    x_high = max(x, x_high)
    y_low = min(y, y_low)
    y_high = max(y, y_high)

  return {
    'x': x_low,
    'w': x_high - x_low,
    'y': y_low,
    'h': y_high - y_low
  }


def PruneShapeRecordToBox(shape_rec, lng_range, lat_range):
  """Returns a copy of the shape_rec, excluding all parts outside the box."""
  shape = shape_rec.shape
  polygons = SplitIntoPolygons(shape)

  ok_polygons = []
  for polygon in polygons:
    cx, cy, A = CenterOfMass(polygon)
    if lng_range[0] < cx < lng_range[1] and lat_range[0] < cy < lat_range[1]:
      ok_polygons.append(polygon)

  assert ok_polygons
  out_shaperec = copy.deepcopy(shape_rec)
  out_shape = out_shaperec.shape
  out_shape.parts = []
  out_shape.points = []
  for polygon in ok_polygons:
    out_shape.parts.append(len(out_shape.points))
    out_shape.points.extend(polygon)

  # TODO(danvk): update out_shape.bbox to be more precise.
  return out_shaperec

# (from http://www.ariel.com.au/a/python-point-int-poly.html)
# determine if a point is inside a given polygon or not
# Polygon is a list of (x,y) pairs.
def point_inside_polygon(x,y,poly):
  n = len(poly)
  inside =False

  p1x,p1y = poly[0]
  for i in range(n+1):
    p2x,p2y = poly[i % n]
    if y > min(p1y,p2y):
      if y <= max(p1y,p2y):
        if x <= max(p1x,p2x):
          if p1y != p2y:
            xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
          if p1x == p2x or x <= xinters:
            inside = not inside
    p1x,p1y = p2x,p2y

  return inside


def PointInPolygon(point, polygon):
  """polygon can be either a list of polygons or a single polygon."""
  try:
    # [ [[lon,lat]] ] vs. [[lon, lat]]
    x = iter(polygon[0][0])
    for p in polygon:
      if PointInPolygon(point, p): return True
    return False
  except TypeError as e:
    for p in polygon:
      assert len(p) == 2, p
    return point_inside_polygon(point[0], point[1], polygon)
