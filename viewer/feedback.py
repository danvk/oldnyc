'''Generic feedback recording system.'''

import uuid
from datetime import datetime, timedelta

import webapp2
from google.appengine.ext import db


class UserFeedback(db.Model):
    photo_id = db.StringProperty()
    feedback = db.TextProperty()
    user_ip = db.StringProperty()
    cookie = db.StringProperty()
    datetime = db.DateTimeProperty(auto_now_add=True)
    user_agent = db.TextProperty()
    location = db.TextProperty()

COOKIE_NAME = 'feedback_cookie'


class RecordFeedback(webapp2.RequestHandler):
    def post(self):
        self.get()
    
    def get(self):
        cookie = None
        if not self.request.cookies.get(COOKIE_NAME):
            cookie = str(uuid.uuid4())
            expire_time = datetime.now() + timedelta(weeks=4)
            self.response.set_cookie(COOKIE_NAME, cookie, expires=expire_time, path='/')
            
        else:
            cookie  = self.request.cookies[COOKIE_NAME]

        headers = self.request.headers
        
        feedback = UserFeedback()
        feedback.photo_id = self.request.get('id')
        feedback.feedback = self.request.get('feedback')

        feedback.user_agent = headers.get('User-Agent')
        feedback.cookie = cookie
        feedback.user_ip = self.request.remote_addr
        feedback.location = '-'.join([headers.get(x, '??') for x in [
            'X-AppEngine-Country', 'X-AppEngine-Region', 'X-AppEngine-City']])

        feedback.put()
        self.response.out.write('OK')


class ClearCookie(webapp2.RequestHandler):
    def post(self):
        self.get()
    
    def get(self):
        self.response.set_cookie(COOKIE_NAME, None)
        self.response.out.write('OK')
