#!/usr/bin/python
# This fixes some of the image URLs in records.pickle.
import record
import re
import cPickle
rs = record.AllRecords()

for idx, r in enumerate(rs):
  url = r.photo_url

  # Some images have thumbnails but are missing the full photo URL.
  # Convert
  #    http://webbie1.sfpl.org/multimedia/thumbnails/aaa9774_x.jpg
  # -> http://webbie1.sfpl.org/multimedia/sfphotos/aaa-9774.jpg
  if not url:
    url = r.thumbnail_url
    if 'aaf' in url:
      # There are only two of these:
      #   http://sflib1.sfpl.org:82/record=b1026391~S0
      #   http://sflib1.sfpl.org:82/record=b1036043~S0
      # They're both links to larger collections of images and don't really fit
      # the mold of the other pages. So we remove them.
      del rs[idx]
      continue
    else:
      # Two of these... I think they're just omissions.
      url = re.sub(r'(.*)/thumbnails/(...)(\d+)_x\.jpg', r'\1/sfphotos/\2-\3.jpg', url)

  # Remove trailing spaces from image URLs.
  # Maybe ~4 of these.
  if url[-1] == ' ':
    url = url[0:-1]

  # Change 'foojpg' -> 'foo.jpg'
  # Just a typo. There are ~4 of these, too.
  if url[-3:] == 'jpg' and url[-4:] != '.jpg':
    print '%s -> %s' % (url, url[:-3] + '.jpg')
    url = url[:-3] + '.jpg'

print "Re-pickling"
output_file = "records.pickle"
f = file(output_file, "w")
p = cPickle.Pickler(f, 2)
for i, r in enumerate(rs):
  p.dump(r)
  if i % 100 == 0:
    print "Pickled %d records" % i
