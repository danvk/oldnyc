import db
import cgi
import logging
import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template


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
      record.image = self.request.get('image')

    record.put()
    self.response.out.write('%s image record %s\n' % (verb, id))

class UploadForm(webapp.RequestHandler):
  def get(self):
    cookie = None
    if 'id' in self.request.cookies:
      cookie = self.request.cookies['id']

    user = None
    if not cookie:
      # Create a new entry for this user and set their cookie.
      user = db.User()
      user.put()
      self.response.headers.add_header(
        'Set-Cookie',
        'id=%s' % user.key(),
        Expires='Wed, 13-Jan-2012 22:23:01 GMT')

    else:
      # Get their record.
      user = db.User.get(cookie)
      assert user

    template_values = {
      'cookie': cookie
    }
    path = os.path.join(os.path.dirname(__file__), 'templates/upload.tpl')
    self.response.out.write(template.render(path, template_values))
