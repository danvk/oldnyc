import cgi
import db
import os
import upload
import random
import logging
from datetime import datetime

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

class MainPage(webapp.RequestHandler):
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
        Expires='Wed, 13-Jan-2021 22:23:01 GMT')

    else:
      # Get their record.
      user = db.User.get(cookie)
      assert user

    # Pull up a random image for them to peruse.
    # We use a combination of user id and time as the random number seed.
    # TODO(danvk): surely there is a better way to do this.
    qs = db.ImageRecord.all().order('-seq_id').fetch(limit=1)
    assert len(qs) == 1
    max_id = qs[0].seq_id
    r = random.Random(str(user.key()) + datetime.now().isoformat())
    id = r.randint(0, max_id)
    logging.info('Showing image %d' % id)
    image = db.ImageRecord.get_by_key_name(str(id))
    assert image

    template_values = {
      'cookie': cookie,
      'image': {
        'id': id,
        'photo_id': image.photo_id,
        'title': image.title,
        'date': image.date,
        'location': image.location,
        'description': image.description,
        'photo_url': image.photo_url
      }
    }
    path = os.path.join(os.path.dirname(__file__), 'templates/mainpage.tpl')
    self.response.out.write(template.render(path, template_values))


class ImageHandler(webapp.RequestHandler):
  def get(self):
    id = self.request.get('id')
    assert id
    
    image = db.ImageRecord.get_by_key_name(id)
    self.response.headers.add_header('Content-type', 'image/jpeg')
    self.response.out.write(image.image)


application = webapp.WSGIApplication(
                                     [
                                      ('/', MainPage),
                                      ('/image', ImageHandler),
                                      ('/upload_form', upload.UploadForm),
                                      ('/upload', upload.UploadHandler)
                                     ],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

