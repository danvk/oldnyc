from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext.db import GeoPt
from google.appengine.ext import db
import os
import logging


def load_folders():
  """Returns a [(count, folder), ...] list."""
  return [(int(line.split("\t")[0]), line.split("\t")[1]) for line in file("folder-counts.txt").read().split("\n")[:-1]]


class GeoCode(db.Model):
  cat = db.StringProperty()
  location = db.GeoPtProperty()
  feasible = db.BooleanProperty()


class MainPage(webapp.RequestHandler):
  def post(self):
    self.get()

  def get(self):
    if self.request.get('cat'):
      gc = GeoCode()
      gc.cat = self.request.get('cat')
      gc.feasible = not not self.request.get('success')
      if gc.feasible:
        lat = self.request.get('lat') 
        lon = self.request.get('lon') 
        assert lat and lon
        gc.location = GeoPt(lat=float(lat), lon=float(lon))
      logging.info('%s, %s : %s' % (gc.feasible, gc.location, gc.cat))
      gc.put()

    folders = load_folders()
    discard = {}
    success = {}
    for geocode in GeoCode.all():
      discard[geocode.cat] = True
      if geocode.feasible:
        success[geocode.cat] = True

    chosen_fold = None
    for count, fold in folders:
      if fold in discard: continue
      subs = fold.split(" / ")
      should_discard = False
      for i in range(1, len(subs)):
        if ' / '.join(subs[0:i]) in discard:
          should_discard = True
          break
      if should_discard: continue

      chosen_fold = fold
      break

    total_done = 0
    for count, fold in folders:
      subs = fold.split(" / ")
      for i in range(1, 1 + len(subs)):
        if ' / '.join(subs[0:i]) in success:
          total_done += count
          break

    template_values = {
      'category': chosen_fold,
      'frequency': count,
      'total_done': total_done
    }
    path = os.path.join(os.path.dirname(__file__), 'mainpage.tpl')
    self.response.out.write(template.render(path, template_values))
      

  

application = webapp.WSGIApplication(
                                     [
                                      ('/', MainPage),
                                     ],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()


