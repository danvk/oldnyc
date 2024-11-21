import pygeojson


def assert_point(g: pygeojson.GeometryObject | None) -> pygeojson.Point:
    if not isinstance(g, pygeojson.Point):
        raise ValueError(f"Expected Point, got {g}")
    return g


def assert_polygon(g: pygeojson.GeometryObject | None) -> pygeojson.Polygon:
    if not isinstance(g, pygeojson.Polygon):
        raise ValueError(f"Expected Point, got {g}")
    return g
