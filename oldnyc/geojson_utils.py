import pygeojson


def assert_point(g: pygeojson.GeometryObject | None) -> pygeojson.Point:
    if not isinstance(g, pygeojson.Point):
        raise ValueError(f"Expected Point, got {g}")
    return g
