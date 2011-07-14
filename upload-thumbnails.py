#!/usr/bin/python
import MultipartPostHandler, urllib2

photo_ids = [line.split('\t')[0] for line in file("/tmp/geocodes-catcodes.txt").read().split("\n") if line]

upload_url = 'http://sf-viewer.appspot.com/upload'
#upload_url = 'http://localhost:8080/upload'

def Upload(pairs):
  global upload_url
  d = {}
  fs = []
  for idx, photo_id in enumerate(pairs):
    d['photo_id%d' % idx] = photo_id
    f = open('thumb/%s.jpg' % photo_id, 'rb')
    d['image%d' % idx] = f
    fs.append(f)

  opener = urllib2.build_opener(MultipartPostHandler.MultipartPostHandler)
  opener.open(upload_url, d)

  for f in fs:
    f.close()


# Get a list of photos that are already there.
response = urllib2.urlopen(upload_url)
text = response.read()
already_uploaded = set(text.split('\n'))
print 'Will skip %d photos which are already uploaded' % len(already_uploaded)

# batch up groups of 20
pairs = []  # (photo_id)
for idx, photo_id in enumerate(photo_ids):
  if photo_id in already_uploaded: continue
  pairs.append(photo_id)

  if len(pairs) == 20:
    Upload(pairs)
    pairs = []
    print 'Uploaded %d' % (1 + idx)

if pairs:
  Upload(pairs)
