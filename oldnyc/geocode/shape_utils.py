# (from http://www.ariel.com.au/a/python-point-int-poly.html)
# determine if a point is inside a given polygon or not
# Polygon is a list of (x,y) pairs.
def point_inside_polygon(x, y, poly):
    n = len(poly)
    inside = False

    p1x, p1y = poly[0]
    for i in range(n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:  # type: ignore
                        inside = not inside
        p1x, p1y = p2x, p2y

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
