"""Construct historic intersections from nyc-streets.geojson"""

import itertools
import sys

import pygeojson
import shapely
from haversine import haversine
from tqdm import tqdm

from oldnyc.geocode.grid import strip_dir


def geom_to_shape(geom: pygeojson.GeometryObject | None):
    if geom is None:
        raise ValueError("Expected geometry, got None")
    if isinstance(geom, pygeojson.LineString):
        return shapely.geometry.LineString(geom.coordinates)
    elif isinstance(geom, pygeojson.MultiLineString):
        return shapely.geometry.MultiLineString(geom.coordinates)
    else:
        raise ValueError(f"Unexpected geometry type: {geom.type}")


def bounds_diam_m(g: shapely.geometry.base.BaseGeometry) -> float:
    lng1, lat1, lng2, lat2 = g.bounds
    return 1000 * haversine((lat1, lng1), (lat2, lng2))


def centroid_if_small(g: shapely.geometry.base.BaseGeometry) -> shapely.geometry.Point | None:
    d_m = bounds_diam_m(g)
    if d_m < 60:
        return g.centroid
    return None


def main():
    streets = pygeojson.load_feature_collection(open("data/originals/nyc-streets.geojson")).features
    geoms = [geom_to_shape(f.geometry) for f in streets]

    for i, j in tqdm(itertools.combinations(range(len(geoms)), 2)):
        name1 = streets[i].properties["name"]
        name2 = streets[j].properties["name"]
        if name1 == name2 or strip_dir(name1) == strip_dir(name2):
            continue
        g1, g2 = geoms[i], geoms[j]
        if not g1.intersects(g2):
            continue
        ix = g1.intersection(g2)
        full_ix = ix
        if not isinstance(ix, shapely.geometry.Point):
            ix = centroid_if_small(ix)
        if not ix:
            sys.stderr.write(
                f'Multiple intersections between "{name1}" ({i}) and "{name2}" ({j}): {full_ix}: {bounds_diam_m(full_ix):.2f}m\n'
            )
            continue

        print(
            "\t".join(
                [
                    str(i),
                    str(j),
                    name1,
                    name2,
                    str(ix.x),
                    str(ix.y),
                ]
            )
        )


if __name__ == "__main__":
    main()
