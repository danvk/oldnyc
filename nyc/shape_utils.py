import math


def _dot(a, b):
  return a[0] * b[0] + a[1] * b[1]

def _norm(x):
    return math.sqrt(_dot(x, x))

def _minus(a, b):
    return (a[0] - b[0], a[1] - b[1])


def DistanceToPolygon(point, points):
    """Returns the distance from a point to the edge of a polygon."""
    minDist = float("inf")
    for p1, p2 in zip(points[:-1], points[1:]):
        p2_p1 = (p2[0] - p1[0], p2[1] - p1[1])
        x_p1 = (point[0] - p1[0], point[1] - p1[1])
        np2_p1 = _norm(p2_p1)
        if np2_p1 == 0:
            continue
        r = 1.0 * _dot(p2_p1, x_p1) / (np2_p1**2)

        if r < 0:
            dist = _norm(x_p1)
        elif r > 1:
            dist = _norm((p2[0] - point[0], p2[1] - point[1]))
        else:
            n = (p2_p1[0] / np2_p1, p2_p1[1] / np2_p1)
            k = _dot(x_p1, n)
            n = (n[0] * k, n[1] * k)
            dist = _norm(_minus(x_p1, n))
            # dist = math.sqrt(_norm2(x_p1) - r * _norm2(p2_p1))
        minDist = min(dist, minDist)

    return minDist


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
        iter(polygon[0][0])
        for p in polygon:
            if PointInPolygon(point, p):
                return True
        return False
    except TypeError:
        for p in polygon:
            assert len(p) == 2, p
        return point_inside_polygon(point[0], point[1], polygon)
