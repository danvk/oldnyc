"""Diff Google and OSM intersections.csv"""

import csv
from collections import defaultdict

from haversine import haversine

Point = tuple[float, float]


def main():
    goog = [*csv.DictReader(open("data/intersections.csv"))]
    osm = [*csv.DictReader(open("data/intersections-osm.csv"))]

    street_ave_to_points = defaultdict[tuple[int, int], list[Point | None]](lambda: [None, None])

    for i, source in enumerate([goog, osm]):
        assert i == 0 or i == 1
        for row in source:
            street = int(row["Street"])
            ave = int(row["Avenue"])
            lat = row["Lat"]
            lon = row["Lon"]
            if lat and lon:
                street_ave_to_points[(street, ave)][i] = (float(lat), float(lon))

    print("Street\tAve\tGoogle\tOSM\tDistance (m)")
    for (street, ave), (goog_point, osm_point) in sorted(street_ave_to_points.items()):
        d_m = 1000
        if goog_point and osm_point:
            d_m = haversine(goog_point, osm_point) * 1000
        if d_m > 40:
            print(f"{street}\t{ave}\t{goog_point}\t{osm_point}\t{d_m:.2f}")


if __name__ == "__main__":
    main()
