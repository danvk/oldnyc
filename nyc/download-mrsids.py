#!/usr/bin/python
'''
The NYPL only provides low-resolution versions of their imagery via the web
viewer. To get high resolution imagery, I need to download it myself. The
high-resolution imagery is only available in the obscure 'MrSID' file format,
which can be converted to JPG using LizardTech's mrsiddecode command line tool.


To download all the MrSID files, I can...
1. Fetch http://images.nypl.org/index.php?id=(image id)&t=d
2. Parse the '&item=' field out of the URL it redirects to
3. Fetch http://lt.images.nypl.org/lizardtech/iserv/getdoc?cat=NYPL&item=(ITEM).sid
4. Convert to JPG: mrsiddecode -i foo.sid -o foo.jpg

Run this from the 'nyc' directory.
'''

import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir) 

import re
import record
import urllib2
import urlparse

VIEWER_PATTERN = 'http://images.nypl.org/index.php?id=%s&t=d'
MRSID_PATTERN = 'http://lt.images.nypl.org/lizardtech/iserv/getdoc?cat=NYPL&item=%s'
IMAGE_DIR = 'images'

# via http://stackoverflow.com/questions/107405/how-do-you-send-a-head-http-request-in-python
class HeadRequest(urllib2.Request):
  def get_method(self):
    return "HEAD"


rs = record.AllRecords('records.pickle')
for idx, rec in enumerate(rs):
  digital_id = rec.photo_id()
  if digital_id[-1] != 'f':
    # TODO(danvk): look at these
    print 'Skipping id %s' % digital_id
    continue

  output_sid = 'images/%s.sid' % digital_id
  output_jpg = 'images/%s.jpg' % digital_id
  if not os.path.exists(output_sid) and not os.path.exists(output_jpg):
    response = urllib2.urlopen(HeadRequest(VIEWER_PATTERN % digital_id))
    o = urlparse.urlparse(response.geturl())
    item_id = urlparse.parse_qs(o.query)['item'][0]
    

    print 'Downloading %s (%s)...' % (output_sid, MRSID_PATTERN % item_id)
    u = urllib2.urlopen(MRSID_PATTERN % item_id)
    localsidfile = open(output_sid, 'w')
    localsidfile.write(u.read())
    localsidfile.close()
    print 'Done!'
