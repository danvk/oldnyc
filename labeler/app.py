import cgi
import db
import os
import upload

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

    template_values = {
      'cookie': cookie
    }
    path = os.path.join(os.path.dirname(__file__), 'templates/mainpage.tpl')
    self.response.out.write(template.render(path, template_values))


application = webapp.WSGIApplication(
                                     [
                                      ('/', MainPage),
                                      ('/upload', upload.UploadHandler)
                                     ],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

