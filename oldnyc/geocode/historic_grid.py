"""Construct historic intersections from nyc-streets.geojson"""

import csv
import itertools
import sys

import pygeojson
import shapely
from haversine import haversine
from tqdm import tqdm

from oldnyc.geocode.grid import Intersection, load_all_intersections, strip_dir


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
    n_ambig, n_match_current, n_match_stripped = 0, 0, 0
    streets = pygeojson.load_feature_collection(open("data/originals/nyc-streets.geojson")).features
    geoms = [geom_to_shape(f.geometry) for f in streets]

    current_ixs, current_stripped_ixs = load_all_intersections()

    out = csv.DictWriter(
        open("data/historic-intersections.csv", "w"),
        fieldnames=["i", "j", "Street1", "Street2", "Borough", "Lat", "Lng"],
    )
    for i, j in tqdm(itertools.combinations(range(len(geoms)), 2)):
        name1 = streets[i].properties["name"]
        name2 = streets[j].properties["name"]
        if name1 == name2 or strip_dir(name1) == strip_dir(name2):
            continue
        g1, g2 = geoms[i], geoms[j]
        if not g1.intersects(g2):
            continue
        pt = g1.intersection(g2)
        full_ix = pt
        if not isinstance(pt, shapely.geometry.Point):
            pt = centroid_if_small(pt)
        if not pt:
            sys.stderr.write(
                f'Multiple intersections between "{name1}" ({i}) and "{name2}" ({j}): {full_ix}: {bounds_diam_m(full_ix):.2f}m\n'
            )
            n_ambig += 1
            continue

        boro1 = streets[i].properties["data"]["borough"]
        boro2 = streets[i].properties["data"]["borough"]
        assert boro1 == boro2, f"{boro1} != {boro2}"

        ix = Intersection(name1, name2, boro1)
        strip_ix = Intersection(strip_dir(name1), strip_dir(name2), boro1)

        if ix in current_ixs:
            n_match_current += 1
            continue

        if strip_ix in current_stripped_ixs:
            n_match_stripped += 1
            continue

        out.writerow(
            {
                "i": str(i),
                "j": str(j),
                "Street1": name1,
                "Street2": name2,
                "Borough": boro1,
                "Lat": str(pt.y),
                "Lng": str(pt.x),
            }
        )

    sys.stderr.write(f"{n_ambig=}, {n_match_current=}, {n_match_stripped=}\n")


if __name__ == "__main__":
    main()
