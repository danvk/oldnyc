# App Engine Console MVC Model
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
import sys
import new
import code
import types
import logging
import cPickle
import StringIO
import datetime
import traceback

from model.session import ShellSession

from google.appengine.ext import db
from google.appengine.api import users

# Types that can't be pickled.
UNPICKLABLE_TYPES = (
    types.ModuleType,
    types.TypeType,
    types.ClassType,
    types.FunctionType,
)


class AppEngineConsole(ShellSession):
    """An interactive console session, derived from the Google shell session example."""
    pending_source = db.TextProperty()
    last_used      = db.DateTimeProperty()

    def __init__(self, *args, **kw):
        ShellSession.__init__(self, *args, **kw)
        self.fresh()

    def storedValue(self, obj):
        """Returns a string representing the given object's value, which should allow the
        code below to determine whether the object changes over time.
        """
        if isinstance(obj, UNPICKLABLE_TYPES):
            return repr(obj)
        else:
            return cPickle.dumps(obj)

    def fresh(self):
        self.out = ''
        self.err = ''
        self.exc_type = None

    def getPending(self):
        if self.pending_source is None:
            return ''
        return self.pending_source
    
    def setPending(self, pending):
        self.pending_source = pending
        self.put()

    def runsource(self, source):
        """Wrap the real source processor to record when the source was processed."""
        try:
            self.last_used = datetime.datetime.now()
            return self.processSource(source)
        finally:
            self.put()

    def processSource(self, source):
        """Runs some source code in the object's context.  The return value will be
        True if the code is valid but incomplete, or False if the code is
        complete (whether by error or not).  If the code is complete, the
        "output" attribute will have the text output of execution (stdout and stderr).
        """
        self.fresh()

        user = users.get_current_user()
        if not user:
            user = '[Unknown User]'
        user = '%s (%s)' % (user, os.environ['REMOTE_ADDR'])

        source = self.getPending() + source
        logging.info('Compiling for: %s >>> %s' % (user, source))

        try:
            bytecode = code.compile_command(source, '<string>', 'single')
        except BaseException, e:
            self.setPending('')
            self.exc_type = type(e)
            self.err = traceback.format_exc()
            logging.info('Compile error for: %s\n%s' % (user, self.err.strip()))
            return False    # Code execution completed (the hard way).

        if bytecode is None:
            logging.debug('Saving pending source for: %s' % user)
            self.setPending('%s\n' % source)
            return True     # Compilation still pending; awaiting lines of code.

        logging.debug('Compilation successful')

        # Create a dedicated module to be used as this statement's __main__.
        statement_module = new.module('__main__')

        # Use this request's __builtin__, since it changes on each request.
        # This is needed for import statements, among other things.
        import __builtin__
        statement_module.__builtins__ = __builtin__

        # Swap in our custom module for __main__, then unpickle the session
        # globals, run the statement, and re-pickle the session globals, all
        # inside it.
        old_main = sys.modules.get('__main__')
        try:
            sys.modules['__main__'] = statement_module
            statement_module.__name__ = '__main__'

            # Re-evaluate the unpicklables.
            for bad_statement in self.unpicklables:
                logging.info(bad_statement)
                exec bad_statement in statement_module.__dict__

            # Re-initialize the globals.
            for name, val in self.globals_dict().items():
                try:
                    statement_module.__dict__[name] = val
                except:
                    msg = 'Dropping %s since it could not be unpickled' % name
                    self.out += '%s\n' % msg
                    logging.warning('%s:\n%s' % (msg, traceback.format_exc()))
                    self.remove_global(name)

            # Execute it.
            buf = StringIO.StringIO()
            old_globals = dict(statement_module.__dict__)

            # Later on, we compare new variable ("global") values to these values to see what's changed
            # and should be saved in the store; however, since old_globals is merely a shallow copy,
            # naively comparing for inequality between old/new values will not work: mutating a list
            # or dict for example will change the underlying object in *both* dicts and so the != comparison
            # will return false.  In other words:
            # >>> a = {'foo': [1, 2]}; b = dict(a); print a['foo'] is b['foo']
            # True
            #
            # The current solution is to remember the object's pickled representation and compare
            # the before and after pickled strings.  Another idea is maybe de-optimizing this completely and
            # just always re-store every global.
            old_global_values = dict([(a, self.storedValue(b)) for a, b in old_globals.items()])

            try:
                old_stdout = sys.stdout
                old_stderr = sys.stderr
                try:
                    sys.stdout = buf
                    sys.stderr = buf
                    exec bytecode in statement_module.__dict__
                finally:
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr
            except BaseException, e:
                # Store the output and user's exception.
                buf.seek(0)
                self.out = buf.read()
                self.err = traceback.format_exc()
                self.exc_type = type(e)
                self.setPending('')
                logging.info('Exception for: %s\nout:\n%s\nerr:\n%s' % (user, self.out.strip(), self.err.strip()))
                return False    # Code execution completed (the hard way).

            buf.seek(0)
            self.out = buf.read()
            logging.info('Execution for: %s: %s' % (user, self.out.strip()))
            self.setPending('')

            # Extract the new globals that this statement added.
            new_globals = {}
            for name, val in statement_module.__dict__.items():
                if name not in old_global_values or self.storedValue(val) != old_global_values[name]:
                    new_globals[name] = val

            if True in [isinstance(val, UNPICKLABLE_TYPES) for val in new_globals.values()]:
                # This statement added an unpicklable global.  Store the statement and
                # the names of all of the globals it added in the unpicklables.
                self.add_unpicklable(source, new_globals.keys())
                logging.debug('Storing this statement as an unpicklable.')
            else:
                # This statement didn't add any unpicklables.  Pickle and store the
                # new globals back into the datastore.
                for name, val in new_globals.items():
                    if not name.startswith('__'):
                        self.set_global(name, val)
        finally:
            sys.modules['__main__'] = old_main

        return False    # Code execution completed.

if __name__ == "__main__":
    logging.error('I should be running unit tests')
