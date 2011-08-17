from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.dist import use_library

import os
import simplejson as json
import logging


class ImageRecord(db.Model):
  # key = photo_id
  photo_id = db.StringProperty()
  title = db.StringProperty()
  date = db.StringProperty()
  folder = db.StringProperty()
  library_url = db.StringProperty()


class ThumbnailRecord(db.Model):
  # key = photo_id
  image = db.BlobProperty()


def GetImageRecords(photo_ids):
  """Queries the ImageRecord db, w/ memcaching. Returns photo_id -> rec dict"""
  # check if we've got the whole thing in memcache
  multi_key = 'MIR' + ','.join(photo_ids)
  recs = memcache.get(multi_key)
  if recs: return recs

  keys = ["IR" + photo_id for photo_id in photo_ids]

  record_map = memcache.get_multi(keys, key_prefix='IR')
  missing_ids = list(set(photo_ids) - set(record_map.keys()))
  if not missing_ids: return record_map

  memcache_map = {}
  db_recs = ImageRecord.get_by_key_name(missing_ids)
  for id, r in zip(missing_ids, db_recs):
    record_map[id] = r
    memcache_map["IR" + id] = r

  if memcache_map:
    memcache.add_multi(memcache_map)
    memcache.add(multi_key, record_map)
  return record_map



class RecordFetcher(webapp.RequestHandler):
  def post(self):
    self.get()

  def get(self):
    """Responds to AJAX requests for record information."""
    photo_ids = self.request.get_all("id")
    default_response = {
      'title': 'Proposed Alemany Blvd. West from Mission St. viaduct, 2-18-26',
      'date': '1926 Feb. 18',
      'folder': 'S.F. Streets / Alemany Boulevard',
      'library_url': 'http://sflib1.sfpl.org:82/record=b1000001~S0'
    }

    rs = GetImageRecords(photo_ids)
    response = {}
    for id, r in rs.iteritems():
      if not r:
        #self.response.out.write("no record for '%s'" % id)
        # This is just to aid local testing:
        response[id] = {
          'title': 'Photo ID #' + id,
          'date': default_response['date'],
          'folder': default_response['folder'],
          'library_url': 'http://sflib1.sfpl.org:82/record=b1000001~S0'
        }
      else:
        response[id] = {
          'title': r.title,
          'date': r.date,
          'folder': r.folder,
          'library_url': r.library_url
        }
    self.response.headers['Cache-Control'] = 'public; max-age=2592000'
    self.response.out.write(json.dumps(response))


#def GetThumbnailRecord(photo_id):
#  """Queries the Thumbnail db, w/ memcaching"""
#  key = "TN" + photo_id
#  r = memcache.get(key)
#  if r: return r
#  r = ThumbnailRecord.get_by_key_name(photo_id)
#  memcache.add(key, r)
#  return r
#
#
#class UploadThumbnailHandler(webapp.RequestHandler):
#  def get(self):
#    # print out a list of photo_ids that we already have.
#    self.response.headers['Content-Type'] = 'text/plain'
#    query = db.Query(ThumbnailRecord, keys_only=True)
#    for thumb in query:
#      self.response.out.write(thumb.name() + "\n")
#
#
#  def post(self):
#    num = 0
#    while self.request.get('photo_id%d' % num):
#      photo_id = self.request.get('photo_id%d' % num)
#      image = self.request.get('image%d' % num)
#      rec = ThumbnailRecord(key_name=photo_id, image=image)
#      rec.put()
#      num += 1
#
#    self.response.out.write('Loaded %d thumbnails' % num)

#class ThumbnailFetcher(webapp.RequestHandler):
#  def get(self):
#    """URL is something like /thumb/AAA-1234.jpg"""
#    basename = os.path.basename(self.request.path)
#    name = basename.split('.')[0]
#    thumb = GetThumbnailRecord(name)
#    if not thumb:
#      self.response.set_status(404)
#      self.response.out.write("Couldn't find image %s" % name)
#      return
#
#    self.response.headers.add_header('Expires', 'Sun, 17-Jan-2038 19:14:07')
#    self.response.headers['Content-type'] = 'image/jpeg'
#    self.response.out.write(thumb.image)



application = webapp.WSGIApplication(
                                     [
                                      ('/info', RecordFetcher),
                                      #('/upload', UploadThumbnailHandler),
                                      #('/thumb.*', ThumbnailFetcher),
                                     ],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

