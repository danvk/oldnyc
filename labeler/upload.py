import db
import cgi
import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app


class UploadHandler(webapp.RequestHandler):
  def post(self):
    """Adds a new image to the DB."""
    self.response.headers.add_header('Content-type', 'text/plain')
    id = self.request.get('id')
    assert id

    verb = 'Updated'
    record = db.ImageRecord.get_by_key_name(id)
    if not record:
      verb = 'Added'
      record = db.ImageRecord(key_name=id)

    props = record.properties()
    for field in ['title', 'date', 'location', 'description', 'photo_url']:
      if self.request.get(field):
        props[field].__set__(record, self.request.get(field))
        self.response.out.write('Set %s\n' % field)
      else:
        self.response.out.write('Leaving %s\n' % field)

    if self.request.get('image'):
      logging.info(type(self.request.get('image')))
      record.image = self.request.get('image')

    record.put()
    self.response.out.write('%s image record %s\n' % (verb, id))

