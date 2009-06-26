#!/usr/bin/python
import glob
import locatable
import re
import record

num = 0
portraits = 0
found = 0
folders = {}
# Could geocode another ~6% of images by hand-labeling the top 50 of these folders:
# TODO(danvk): geocode these manually.
interesting = [
  'Folder: S.F. Churches',
  'Folder: S.F. Hotels',
  'Folder: S.F. Schools',
  'Folder: S.F. Theaters',
  'Folder: S.F. Businesses',
  'Folder: S.F. Monuments',
  'Folder: S.F. Stadiums',
  'Folder: S.F. Libraries',
  'Folder: S.F. Colleges',
  'Folder: S.F. Islands',
]

for filename in glob.glob("records/*"):
  r = record.Record.FromString(file(filename).read())
  if not r: continue
  if r.location and "Folder: Portraits" in r.location:
    portraits += 1
    continue

  num += 1
  if locatable.IsLocatable(r):
    print r.preferred_url
    found += 1

  if r.location:
    for loc in interesting:
      if loc in r.location:
        l = r.location
        l = re.sub(r'-?\(.*', '', l)
        folders[l] = 1 + folders.setdefault(l, 0)

print "Skipped %d portraits" % portraits
print "Could locate %d/%d = %f records" % (found, num, 1.0 * found / num)
locatable.PrintLocationStats()

print "Common folders:"
by_count = []
for (k, v) in folders.iteritems():
  if v > 2:
    by_count.append((v,k))
for (v, k) in reversed(sorted(by_count)):
  print "  %6d (%0.2f%%) %s" % (v, 100.0*v/num, k)
