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

from os.path import dirname, join, abspath
import sys

def addPath(dir):
    if dir not in sys.path:
        sys.path.insert(0, dir)

thisFile    = abspath(__file__)
thisDir     = dirname(thisFile)
appPath     = abspath(join(thisDir, '..', '..'))
consolePath = join(appPath, 'console', 'app')
gaePath     = abspath(join(appPath, '..', 'google_appengine'))
gaeLibPath  = join(gaePath, 'lib')
yamlPath    = join(gaeLibPath, 'yaml', 'lib')
webobPath   = join(gaeLibPath, 'webob')
djangoPath  = join(gaeLibPath, 'django')

# Go in reverse priority order due to to the insertion mechanism.
for dir in (consolePath, appPath, gaePath, yamlPath, webobPath, djangoPath):
    addPath(dir)
