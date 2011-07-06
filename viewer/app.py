from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext.db import GeoPt
from google.appengine.ext import db
import os
import simplejson as json
import logging


def load_entries():
  """Returns a [(count, folder), ...] list."""
  return [(int(line.split("\t")[0]), line.split("\t")[1]) for line in file("folder-counts.txt").read().split("\n")[:-1]]


class ImageRecord(db.Model):
  # key = photo_id
  photo_id = db.StringProperty()
  title = db.StringProperty()
  date = db.StringProperty()
  folder = db.StringProperty()
  library_url = db.StringProperty()


class MainPage(webapp.RequestHandler):
  def get(self):
    num = 0
    for r in ImageRecord.all():
      num += 1
    self.response.out.write('Serving %d records' % num)


class RecordFetcher(webapp.RequestHandler):
  def get(self):
    """Responds to AJAX requests for record information."""
    id = self.request.get("id")
    response = {
      'title': 'Proposed Alemany Blvd. West from Mission St. viaduct, 2-18-26',
      'date': '1926 Feb. 18',
      'folder': 'S.F. Streets / Alemany Boulevard',
      'library_url': 'http://sflib1.sfpl.org:82/record=b1000001~S0'
    }
    if not id:
      #self.response.out.write("no 'id' param")
      pass
    else:
      r = ImageRecord.get_by_key_name(id)
      if not r:
        #self.response.out.write("no record for '%s'" % id)
        pass
      else:
        response = {
          'title': r.title,
          'date': r.date,
          'folder': r.folder,
          'library_url': r.library_url
        }
    self.response.out.write(json.dumps(response))


application = webapp.WSGIApplication(
                                     [
                                      ('/', MainPage),
                                      ('/info', RecordFetcher),
                                     ],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()


