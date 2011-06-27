import cgi
import db
import os
import upload
import labeler
import logging
from datetime import datetime

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext.db import GeoPt


class MainPage(webapp.RequestHandler):
  def get(self):
    user = labeler.userFromCookie(self)
    assert user

    if not self.request.get('id'):
      # Redirect them to a random image.
      id = labeler.randomImage(user)
      self.redirect('/?id=%d' % id)
      return

    id = int(self.request.get('id'))
    logging.info('Showing record %d to %s' % (id, user.key()))
    image = db.ImageRecord.get_by_key_name(str(id))
    assert image

    carousel = labeler.nearbyIds(user, id)

    template_values = {
      'cookie': str(user.key()),
      'image': {
        'id': id,
        'photo_id': image.photo_id,
        'title': image.title,
        'date': image.date,
        'folder': image.folder,
        'description': image.description,
        'note': image.note,
        'library_url': image.library_url
      },
      'carousel': [
        {
          'id': this_id,
          'current': (id == this_id)
        } for this_id in carousel
      ]
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


class GeocodeHandler(webapp.RequestHandler):
  def post(self):
    cookie = self.request.get('cookie')
    if not cookie:
      logging.warning('Submit to /geocode without cookie.')
      self.redirect('/')
      return

    user = db.User.get(cookie)
    assert user

    assert self.request.get('id')
    photo = db.ImageRecord.get_by_key_name(self.request.get('id'))
    assert photo

    geocode = db.Geocode(user=user, photo=photo)

    lat = self.request.get('lat') 
    lon = self.request.get('lon') 
    if lat and lon:
      geocode.location = GeoPt(lat=float(lat), lon=float(lon))

    if self.request.get('impossible'):
      geocode.feasibility = 'no'
    elif self.request.get('notme'):
      geocode.feasibility = 'maybe'
    elif self.request.get('notsf'):
      geocode.feasibility = 'notsf'
    elif self.request.get('success'):
      geocode.feasibility = 'yes'
    else:
      logging.warning('Got rating w/o feasibility')
      self.redirect('/')
      return

    setting = self.request.get('setting')
    if setting: geocode.setting = setting

    rating = self.request.get('rating')
    if rating:
      rating = int(rating)
      if rating >= 1 and rating <= 5:
        geocode.rating = rating
      else:
        logging.warning('Got odd rating: %s' % rating)

    comments = self.request.get('comments')
    if comments:
      geocode.comments = comments

    geocode.put()
    logging.info('Geocode %s for %s by %s' % (
        geocode.feasibility, photo.photo_id, user.key()))

    # Take them to another random image.
    id = labeler.randomImage(user)
    self.redirect('/?id=%d' % id)
    

application = webapp.WSGIApplication(
                                     [
                                      ('/', MainPage),
                                      ('/image', ImageHandler),
                                      ('/geocode', GeocodeHandler),
                                      ('/upload_form', upload.UploadForm),
                                      ('/upload', upload.UploadHandler)
                                     ],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

