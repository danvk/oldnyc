#!/usr/bin/env python
"""
Reads in locations.txt (produced by geocode.py with --output_mode=locations.txt)
and clusters very close points. This reduces the number of unique map markers and
makes it easier to find things.

Output is an exhaustive mapping of "old_lat,old_lon\tnew_lat,new_lon" pairs.

TODO:
- remove large catcodes from consideration
- break up clusters which have grown too large
- look over pre-built eval pairs
- implement this as a hook for lat-lons.js
- look at before/after
"""

import fileinput

# TODO: move to argparse
DISTANCE_THRESHOLD = 20

# TODO: move to argparse
output_mode = "map"  # 'urls'

counts = []
lat_lons = []
orig_points = 0
for line in fileinput.input():
    line = line.strip()
    if not line:
        continue
    orig_points += 1
    count, ll = line.split("\t")
    lat, lon = [float(x) for x in ll.split(",")]
    count = int(count)

    counts.append(count)
    lat_lons.append((lat, lon))


def UrlForIndex(idx):
    global lat_lons
    lat, lon = lat_lons[idx]
    return "http://localhost:8080/#ll:%.6f|%.6f,m:%.5f|%.5f|19" % (lat, lon, lat, lon)


def dist(a, b):
    d1 = a[0] - b[0]
    d2 = a[1] - b[1]
    return 1.0e8 * (d1 * d1 + d2 * d2)


def centroidForIndices(idxs):
    global lat_lons, counts
    lat_sum = 0
    lon_sum = 0
    total = 0
    for i in idxs:
        ll = lat_lons[i]
        lat_sum += ll[0] * counts[i]
        lon_sum += ll[1] * counts[i]
        total += counts[i]

    return (lat_sum / total, lon_sum / total)


# calculate all-pairs distances
nns = []  # index -> list of (distance, index) neighbors
for i in range(0, len(lat_lons)):
    neighbors = []  # (dist, index)
    a = lat_lons[i]
    for j in range(i + 1, len(lat_lons)):
        b = lat_lons[j]
        d = dist(a, b)
        if d > DISTANCE_THRESHOLD:
            continue
        neighbors.append((-d, j))
    neighbors.sort()

    nns.append([(-x[0], x[1]) for x in neighbors])


# we hope there aren't any really degenerate cases
cluster_map = {}  # idx -> cluster representative idx
for i, buds in enumerate(nns):
    if not buds:
        continue

    cluster_idx = i
    if i in cluster_map:
        cluster_idx = cluster_map[i]
    for d, j in buds:
        if j in cluster_map:
            if cluster_map[j] != cluster_idx:
                old_idx = cluster_map[j]
                for idx, rep in cluster_map.items():
                    if rep == old_idx:
                        cluster_map[idx] = cluster_idx
                cluster_map[old_idx] = cluster_idx
                # this is pathological behavior; we artificially break the cluster
                # a = j
                # b = cluster_map[j]
                # c = cluster_idx
                # ll = lat_lons[a]
                # print '    Current: %d = 0.000 %s %s' % (a, ll, UrlForIndex(b))
                # print 'Old cluster: %d = %.3f %s %s' % (
                #    b, dist(ll, lat_lons[b]), lat_lons[b], UrlForIndex(b))
                # print 'New cluster: %d = %.3f %s %s' % (
                #    c, dist(ll, lat_lons[c]), lat_lons[c], UrlForIndex(c))
                # assert False
        cluster_map[j] = cluster_idx


clusters = {}  # representative idx -> list of constituent indices
for i, rep in cluster_map.items():
    if rep not in clusters:
        clusters[rep] = [rep]
    clusters[rep].append(i)


if output_mode == "map":
    for base, members in clusters.items():
        ll = centroidForIndices(members)
        for i in members:
            b = lat_lons[i]
            print("%.6f,%.6f->%.6f,%.6f" % (b[0], b[1], ll[0], ll[1]))


if output_mode == "urls":
    num_points = 0
    for base, members in clusters.items():
        if not members:
            continue
        print("(%d)" % len(members))
        for i in members:
            print("  %s" % UrlForIndex(i))
        print()
        num_points += len(members)

    print("%d clusters, %d/%d points" % (len(clusters), num_points, orig_points))
