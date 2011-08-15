#!/usr/bin/python
"""
Reads in locations.txt (produced by generate-geocodes.py with
--output_mode=locations.txt) and clusters very close points. This reduces the
number of unique map markers and makes it easier to find things.

Output is an exhaustive mapping of "old_lat,old_lon\tnew_lat,new_lon" pairs.
"""
from collections import defaultdict
import fileinput

# (lat, lon) -> count
counts = {}
lat_lons = []
for line in fileinput.input():
  line = line.strip()
  if not line: continue
  count, ll = line.split('\t')
  lat, lon = [float(x) for x in ll.split(',')]

  counts[(lat, lon)] = count
  lat_lons.append((lat, lon))


def UrlForIndex(idx):
  global lat_lons
  lat, lon = lat_lons[idx]
  return 'http://oldsf.org/#ll:%.6f|%.6f,m:%.5f|%.5f|19' % (lat, lon, lat, lon)


def dist(a, b):
  d1 = a[0] - b[0]
  d2 = a[1] - b[1]
  return 1.0e8 * (d1*d1 + d2*d2)


# calculate all-pairs distances
nns = []  # index -> list of (distance, index) neighbors
for i in range(0, len(lat_lons)):
  neighbors = []  # (dist, index)
  a = lat_lons[i]
  for j in range(i + 1, len(lat_lons)):
    b = lat_lons[j]
    d = dist(a, b)
    if d > 4: continue
    neighbors.append((-d, j))
  neighbors.sort()

  nns.append([(-x[0], x[1]) for x in neighbors[:10]])

# we hope there aren't any really degenerate cases
cluster_map = {}    # idx -> cluster representative idx
for i, buds in enumerate(nns):
  if not buds: continue

  cluster_idx = i
  if i in cluster_map: cluster_idx = cluster_map[i]
  for d, j in buds:
    if j in cluster_map:
      if cluster_map[j] != cluster_idx:
        old_idx = cluster_map[j]
        for idx, rep in cluster_map.iteritems():
          if rep == old_idx: cluster_map[idx] = cluster_idx
        # this is pathological behavior; we artificially break the cluster
        #a = j
        #b = cluster_map[j]
        #c = cluster_idx
        #ll = lat_lons[a]
        #print '    Current: %d = 0.000 %s %s' % (a, ll, UrlForIndex(b))
        #print 'Old cluster: %d = %.3f %s %s' % (
        #    b, dist(ll, lat_lons[b]), lat_lons[b], UrlForIndex(b))
        #print 'New cluster: %d = %.3f %s %s' % (
        #    c, dist(ll, lat_lons[c]), lat_lons[c], UrlForIndex(c))
        #assert False
    cluster_map[j] = cluster_idx


clusters = {}  # representative idx -> list of constituent indices
for i, rep in cluster_map.iteritems():
  if rep not in clusters:
    clusters[rep] = [rep]
  clusters[rep].append(i)


for base, members in clusters.iteritems():
  if not members: continue
  print '(%d)' % len(members)
  for i in members:
    print '  %s' % UrlForIndex(i)
  print ''
