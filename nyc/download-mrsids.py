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
import time
import urllib
import urllib2
import urlparse
import subprocess

CONVERT_CMD = 'mrsiddecode -i %s -o %s'

VIEWER_PATTERN = 'http://images.nypl.org/index.php?id=%s&t=d'
MRSID_PATTERN = 'http://lt.images.nypl.org/lizardtech/iserv/getdoc?cat=NYPL&item=%s'
IMAGE_DIR = sys.argv[1]

# via http://stackoverflow.com/questions/107405/how-do-you-send-a-head-http-request-in-python
class HeadRequest(urllib2.Request):
  def get_method(self):
    return "HEAD"


def GetRedirect(url):
  location_header = 'location: '
  output = subprocess.check_output(['curl', '--silent', '-I', url])
  for line in output.split('\n'):
    if line.startswith(location_header):
      return line[len(location_header):].strip()
  return None


rs = record.AllRecords('records.pickle')
for idx, rec in enumerate(rs):
  digital_id = rec.photo_id()
  # if digital_id[-1] != 'f':
  #   # TODO(danvk): look at these
  #   print 'Skipping id %s' % digital_id
  #   continue

  output_sid = '%s/%s.sid' % (IMAGE_DIR, digital_id)
  output_jpg = '%s/%s.jpg' % (IMAGE_DIR, digital_id)
  if not os.path.exists(output_sid) and not os.path.exists(output_jpg):
    viewer_url = VIEWER_PATTERN % urllib.quote_plus(digital_id)
    # print '%s: %s' % (digital_id, viewer_url)
    # response = urllib2.urlopen(HeadRequest(viewer_url))
    # o = urlparse.urlparse(response.geturl())
    # item_id = urlparse.parse_qs(o.query)['item'][0].strip()
    redirect_url = GetRedirect(viewer_url)
    if not redirect_url:
      sys.stderr.write('%s: Unable to get redirect URL' % digital_id)
      continue
    q_fields = urlparse.parse_qs(redirect_url)
    if 'item' not in q_fields:
      sys.stderr.write('%s: Unable to parse item_id from URL %s\n' % (digital_id, redirect_url))
      continue
    item_id = q_fields['item'][0]

    tmp_file = output_sid + '.tmp'
    sid_url = MRSID_PATTERN % item_id
    print 'Downloading %s (%s)...' % (output_sid, sid_url)
    try:
      u = urllib2.urlopen(sid_url)
      localsidfile = open(tmp_file, 'w')
      localsidfile.write(u.read())
      localsidfile.close()
      os.rename(tmp_file, output_sid)
      print 'Done!'
    except urllib2.HTTPError as e:
      sys.stderr.write('ERROR: Unable to fetch %s\n' % sid_url)
      sys.stderr.write('(Skipping)\n')
    time.sleep(2)
