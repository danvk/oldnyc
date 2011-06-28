import labeler_db
import cgi
import logging
import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.api import memcache

kProps = ['photo_id', 'title', 'date', 'folder', 'description', 'note', 'library_url']

class UploadHandler(webapp.RequestHandler):
  def post(self):
    """Adds a new image to the DB."""
    self.response.headers.add_header('Content-type', 'text/plain')
    id = self.request.get('seq_id')
    assert id
    assert int(id) >= 0

    verb = 'Updated'
    record = labeler_db.ImageRecord.get_by_key_name(id)
    if not record:
      verb = 'Added'
      record = labeler_db.ImageRecord(key_name=id)

    record.seq_id = int(id)
    props = record.properties()
    for field in kProps:
      if self.request.get(field):
        props[field].__set__(record, self.request.get(field))

    if self.request.get('image'):
      record.image = self.request.get('image')

    record.put()
    memcache.delete('max_id')  # might not be valid any more.
    self.response.out.write('%s image record %s\n' % (verb, id))


class UploadForm(webapp.RequestHandler):
  def get(self):
    cookie = None
    if 'id' in self.request.cookies:
      cookie = self.request.cookies['id']

    user = None
    if not cookie:
      # Create a new entry for this user and set their cookie.
      user = labeler_db.User()
      user.put()
      self.response.headers.add_header(
        'Set-Cookie',
        'id=%s' % user.key(),
        Expires='Wed, 13-Jan-2012 22:23:01 GMT')

    else:
      # Get their record.
      user = labeler_db.User.get(cookie)
      assert user

    template_values = {
      'cookie': cookie
    }
    path = os.path.join(os.path.dirname(__file__), 'templates/upload.tpl')
    self.response.out.write(template.render(path, template_values))
