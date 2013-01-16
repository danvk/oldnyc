#from google.appengine.ext import webapp
import webapp2
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

import os
import simplejson as json
import logging

# See https://developers.google.com/appengine/docs/python/runtime#The_Environment
VERSION = os.environ['CURRENT_VERSION_ID']


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
  multi_key = VERSION + 'MIR' + ','.join(photo_ids)
  recs = memcache.get(multi_key)
  if recs: return recs

  keys_no_prefix = photo_ids[:]
  key_prefix = VERSION + 'IR'

  record_map = memcache.get_multi(keys_no_prefix, key_prefix=key_prefix)
  missing_ids = list(set(keys_no_prefix) - set(record_map.keys()))
  if not missing_ids: return record_map

  config = db.create_config(read_policy=db.EVENTUAL_CONSISTENCY)
  db_recs = ImageRecord.get_by_key_name(missing_ids, config=config)

  memcache_map = {}
  for id, r in zip(missing_ids, db_recs):
    record_map[id] = r
    memcache_map[id] = r

  if memcache_map:
    memcache.add_multi(memcache_map, key_prefix=key_prefix)
    memcache.add(multi_key, record_map)
  return record_map


class RecordFetcher(webapp2.RequestHandler):
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
          'title': 'Pat and Mike Dugan running around their aunt, Carla Vanni, in Washington Square Park who was super awesome!',  # 'Photo ID #' + id,
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


class AddEgg(webapp2.RequestHandler):
  def get(self):
    image = ImageRecord(key_name="egg")
    image.photo_id = 'egg'
    image.title = 'Old S.F. developers with their handywork'
    image.date = 'August 17, 2011'
    image.folder = 'The New York Collection'
    image.library_url = 'http://danvk.org/'
    image.put()


app = webapp2.WSGIApplication(
                              [
                               ('/info', RecordFetcher),
                               #('/upload', UploadThumbnailHandler),
                               #('/thumb.*', ThumbnailFetcher),
                               ('/addegg', AddEgg),
                              ],
                              debug=True)

# def main():
#     run_wsgi_app(application)
# 
# if __name__ == "__main__":
#     main()

