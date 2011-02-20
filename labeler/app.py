import db
import cgi

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

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

    self.response.out.write('<html><body>uid: %s</boby></html>' % user.key())


application = webapp.WSGIApplication(
                                     [('/', MainPage)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

