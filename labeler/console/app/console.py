# The WSGI entry-point for App Engine Console
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
import re
import sys
import cgi
import code
import logging

from os.path import join, dirname
sys.path.insert(0, dirname(__file__))
sys.path.insert(0, dirname(dirname(__file__)))

import util
import controller

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

debug = util.is_dev()
application = webapp.WSGIApplication([
    ('/'                  , controller.Root),
    ('/console/dashboard/', controller.Dashboard),
    ('/console/help.*'    , controller.Help),
    ('/console/statement' , controller.Statement),
    ('/console/banner'    , controller.Banner),
    ('/console.*'         , controller.Console),
], debug=debug)

def main():
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
