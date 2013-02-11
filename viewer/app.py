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
try:
  VERSION = os.environ['CURRENT_VERSION_ID']
except:
  VERSION = ''


class ImageRecord(db.Model):
  # key = photo_id
  photo_id = db.StringProperty()
  title = db.StringProperty()
  date = db.StringProperty()
  folder = db.StringProperty()
  library_url = db.StringProperty()
  width = db.IntegerProperty()
  height = db.IntegerProperty()
  description = db.StringProperty()
  note = db.StringProperty()


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
      'title': 'Pat and Mike Dugan running around their aunt, Carla Vanni, in Washington Square Park who was super awesome!',
      'date': '1926 Feb. 18',
      'folder': 'S.F. Streets / Alemany Boulevard',
      'library_url': 'http://sflib1.sfpl.org:82/record=b1000001~S0',
      'width': 474,
      'height': 400
    }

    rs = GetImageRecords(photo_ids)
    response = {}
    for id, r in rs.iteritems():
      if not r:
        #self.response.out.write("no record for '%s'" % id)
        # This is just to aid local testing:
        response[id] = default_response.copy()
      else:
        title = r.title
        if r.description:
          title += '; ' + r.description
        if r.note:
          title += '; ' + r.note
        response[id] = {
          'title': title,
          'date': r.date,
          'folder': r.folder,
          'library_url': r.library_url,
          'width': r.width,
          'height': r.height
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


class AddDims(webapp2.RequestHandler):
  def get(self):
    self.post()

  def post(self):
    recs = self.request.get_all('d')
    photo_id_to_dims = {}
    for rec in recs:
      photo_id, width_str, height_str = rec.split(',')
      width = int(width_str)
      height = int(height_str)
      photo_id_to_dims[photo_id] = (width, height)

    config = db.create_config(read_policy=db.EVENTUAL_CONSISTENCY)
    db_recs = ImageRecord.get_by_key_name(photo_id_to_dims.keys(), config=config)

    for image in db_recs:
      width, height = photo_id_to_dims[image.photo_id]
      if image.width == width and image.height == height:
        continue
      image.width = width
      image.height = height
      image.put()

    self.response.out.write('Added %d dimensions' % len(db_recs))


kProps = ['photo_id', 'title', 'date', 'folder', 'note', 'library_url', 'description', 'note']
kIntProps = ['width', 'height']

class UploadHandler(webapp2.RequestHandler):
  def post(self):
    """Adds a new image to the DB."""
    self.response.headers.add_header('Content-type', 'text/plain')
    recs = self.request.get_all('r')
    for rec_json in recs:
      rec = json.loads(rec_json)
      id = rec['photo_id']
      assert id

      verb = 'Updated'
      record = ImageRecord.get_by_key_name(id)
      if not record:
        verb = 'Added'
        record = ImageRecord(key_name=id)

      props = record.properties()
      for field in kProps:
        if field in rec:
          props[field].__set__(record, rec[field])
      for field in kIntProps:
        if field in rec:
          props[field].__set__(record, int(rec[field]))

      record.put()
      self.response.out.write('%s image record %s\n' % (verb, id))


app = webapp2.WSGIApplication(
                              [
                               ('/info', RecordFetcher),
                               ('/upload', UploadHandler),
                               #('/thumb.*', ThumbnailFetcher),
                               ('/addegg', AddEgg),
                               #('/adddims', AddDims),
                              ],
                              debug=True)

# def main():
#     run_wsgi_app(application)
# 
# if __name__ == "__main__":
#     main()

