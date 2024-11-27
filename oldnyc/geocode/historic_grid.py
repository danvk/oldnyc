"""Construct historic intersections from nyc-streets.geojson"""

import csv
import itertools
import sys
from collections import defaultdict

import pygeojson
import shapely
from haversine import haversine
from tqdm import tqdm

from oldnyc.geocode.geocode_types import Point
from oldnyc.geocode.grid import (
    Intersection,
    load_all_intersections,
    normalize_street_for_osm,
    strip_dir,
)


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

    current_ixs, current_stripped_ixs = load_all_intersections(exclude_historic=True)

    ix_to_pt = defaultdict[Intersection, list[Point]](list)
    for i, j in tqdm(itertools.combinations(range(len(geoms)), 2)):
        name1 = normalize_street_for_osm(streets[i].properties["name"])
        name2 = normalize_street_for_osm(streets[j].properties["name"])
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

        ix_to_pt[ix].append((pt.y, pt.x))

    out = csv.DictWriter(
        open("data/historic-intersections.csv", "w"),
        fieldnames=["i", "j", "Street1", "Street2", "Borough", "Lat", "Lon"],
    )
    out.writeheader()
    n_ambig_dedupe = 0
    for ix, pts in ix_to_pt.items():
        mp = shapely.geometry.MultiPoint([(x, y) for (y, x) in pts])
        pt = centroid_if_small(mp)
        if not pt:
            sys.stderr.write(f"Skipping {ix} with {len(pts)} points: {mp} / {bounds_diam_m(mp)}m\n")
            n_ambig_dedupe += 1
            continue
        out.writerow(
            {
                "Street1": ix.str1,
                "Street2": ix.str2,
                "Borough": ix.boro,
                "Lat": str(pt.y),
                "Lon": str(pt.x),
            }
        )
    sys.stderr.write(f"{n_ambig=}, {n_match_current=}, {n_match_stripped=}, {n_ambig_dedupe=}\n")


if __name__ == "__main__":
    main()
