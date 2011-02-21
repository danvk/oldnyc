import cgi
import db
import os
import upload
import random

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
    ks = [k for k in db.ImageRecord.all(keys_only=True)]
    k = random.choice(ks)
    image = db.ImageRecord.get(k)
    assert image

    template_values = {
      'cookie': cookie,
      'image': {
        'photo_id': k.name(),
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

