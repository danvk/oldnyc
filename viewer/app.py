#from google.appengine.ext import webapp
import webapp2
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

import base64
import os
import logging

import feedback


# See https://developers.google.com/appengine/docs/python/runtime#The_Environment
try:
  VERSION = os.environ['CURRENT_VERSION_ID']
except:
  VERSION = ''


app = webapp2.WSGIApplication(
                              [
                               ('/rec_feedback', feedback.RecordFeedback),
                              ],
                              debug=True)

# def main():
#     run_wsgi_app(application)
# 
# if __name__ == "__main__":
#     main()

