#!/usr/bin/python
#
# Go through the image-sizes.txt file and upload image
# height/width to AppEngine.
#
# Usage:
# ./upload-dimensions.py image-sizes.txt http://localhost:8080/adddims

import re
import sys
import urllib2

sizes_path, post_url = sys.argv[1:]

CHUNK_SIZE = 100  # number of dimensions to set per HTTP POST

# via http://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks-in-python
def chunks(l, n):
  '''Yield successive n-sized chunks from l.'''
  for i in xrange(0, len(l), n):
    yield l[i:i+n]


total = 0
for lines in chunks(file(sizes_path).readlines(), CHUNK_SIZE):
  data = 'd=' + '&d='.join([x.strip() for x in lines])
  msg = urllib2.urlopen(post_url, data).read()
  m = re.search(r'(\d+) dimensions', msg)
  assert m
  count = int(m.group(1))
  assert count == len(lines)

  total += len(lines)
  print 'Set %d dimensions' % total

