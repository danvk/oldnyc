#!/usr/bin/env python
#
# testpaths.py - Set up the correct sys.path for the test suite to run.
#
# Copyright 2008-2009 Proven Corporation Co., Ltd., Thailand
#
# This file is part of App Engine Console.
#
# App Engine Console is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# App Engine Console is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with App Engine Console; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import os
import time
import unittest
import test_environment

from google.appengine.api import apiproxy_stub_map
from google.appengine.api import datastore_file_stub
from google.appengine.api import mail_stub
from google.appengine.api import urlfetch_stub
from google.appengine.api import user_service_stub
#from google3.apphosting.api import urlfetch_stub
#from google3.apphosting.api import user_service_stub

APP_ID = u'test_app'
AUTH_DOMAIN = 'gmail.com'
LOGGED_IN_USER = 'test@example.com'  # set to '' for no logged in user

def initialSetup():
    """This needs to run once before any app engine code runs to set up the environment."""
    os.environ['TZ']                 = 'UTC'
    os.environ['USER_EMAIL']         = LOGGED_IN_USER
    os.environ['AUTH_DOMAIN']        = AUTH_DOMAIN
    os.environ['REMOTE_ADDR']        = '127.0.0.1'
    os.environ['APPLICATION_ID']     = APP_ID
    os.environ['SERVER_SOFTWARE']    = 'App Engine Testing'
    os.environ['CURRENT_VERSION_ID'] = os.environ['app_version']

class AppEngineTest(unittest.TestCase):
    def setUp(self):
        # Ensure we're in UTC.
        time.tzset()

        # Start with a fresh api proxy.
        apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()

        # Use a fresh stub datastore.
        stub = datastore_file_stub.DatastoreFileStub(APP_ID, '/dev/null', '/dev/null')
        apiproxy_stub_map.apiproxy.RegisterStub('datastore_v3', stub)

        # Use a fresh stub UserService.
        apiproxy_stub_map.apiproxy.RegisterStub('user', user_service_stub.UserServiceStub())

        # Use a fresh urlfetch stub.
        apiproxy_stub_map.apiproxy.RegisterStub('urlfetch', urlfetch_stub.URLFetchServiceStub())

        # Use a fresh mail stub.
        apiproxy_stub_map.apiproxy.RegisterStub('mail', mail_stub.MailServiceStub()) 

initialSetup()
