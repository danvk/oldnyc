#from google.appengine.ext import webapp
import webapp2
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

import base64
import os
import simplejson as json
import logging

# See https://developers.google.com/appengine/docs/python/runtime#The_Environment
try:
  VERSION = os.environ['CURRENT_VERSION_ID']
except:
  VERSION = ''

MEMCACHE_ENABLED = not os.environ['SERVER_SOFTWARE'].startswith('Development')


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
  keys_no_prefix = photo_ids[:]
  if MEMCACHE_ENABLED:
    multi_key = VERSION + 'MIR' + ','.join(photo_ids)
    recs = memcache.get(multi_key)
    if recs: return recs

    key_prefix = VERSION + 'IR'

    record_map = memcache.get_multi(keys_no_prefix, key_prefix=key_prefix)
    missing_ids = list(set(keys_no_prefix) - set(record_map.keys()))
    if not missing_ids: return record_map
  else:
    missing_ids = keys_no_prefix
    record_map = {}

  config = db.create_config(read_policy=db.EVENTUAL_CONSISTENCY)
  db_recs = ImageRecord.get_by_key_name(missing_ids, config=config)

  memcache_map = {}
  for id, r in zip(missing_ids, db_recs):
    record_map[id] = r
    memcache_map[id] = r

  if MEMCACHE_ENABLED and memcache_map:
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
      'title': '(not here yet!)',
      'date': '1926 Feb. 18',
      'folder': 'S.F. Streets / Alemany Boulevard',
      'library_url': 'http://sflib1.sfpl.org:82/record=b1000001~S0',
      'width': 600,
      'height': 500
    }

    rs = GetImageRecords(photo_ids)
    response = {}
    for id, r in rs.iteritems():
      if not r:
        #self.response.out.write("no record for '%s'" % id)
        # This is just to aid local testing:
        response[id] = default_response.copy()
        orig_id = id.split('-')[0]
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

# From http://stackoverflow.com/questions/9461085/password-protect-static-page-appengine-howto
def basicAuth(func):
  def callf(webappRequest, *args, **kwargs):
    # Parse the header to extract a user/password combo.
    # We're expecting something like "Basic XZxgZRTpbjpvcGVuIHYlc4FkZQ=="
    auth_header = webappRequest.request.headers.get('Authorization')

    if auth_header == None:
      webappRequest.response.set_status(401, message="Authorization Required")
      webappRequest.response.headers['WWW-Authenticate'] = 'Basic realm="OldNYC"'
    else:
      # Isolate the encoded user/passwd and decode it
      auth_parts = auth_header.split(' ')
      user_pass_parts = base64.b64decode(auth_parts[1]).split(':')
      user_arg = user_pass_parts[0]
      pass_arg = user_pass_parts[1]

      if user_arg != "robert" or pass_arg != "moses":
        webappRequest.response.set_status(401, message="Authorization Required")
        webappRequest.response.headers['WWW-Authenticate'] = 'Basic realm="Secure Area"'
        # Rendering a 401 Error page is a good way to go...
        self.response.out.write('sorry!', {})
      else:
        return func(webappRequest, *args, **kwargs)

  return callf

class RootHandler(webapp2.RequestHandler):
  @basicAuth
  def get(self):
    logging.info('hello')
    self.response.headers['Content-type'] = 'text/html'
    self.response.out.write(open('static/viewer.html').read())


app = webapp2.WSGIApplication(
                              [
                               ('/', RootHandler),
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

