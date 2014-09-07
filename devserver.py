#!/usr/bin/env python
'''A flask server which serves static files according to AppEngine's app.yaml.

This helps you transition away from AppEngine!
'''

import os
import re
import sys
import yaml
from flask import Flask, send_from_directory, request

def make_app(yaml_file, script_handler):
    app_yaml_dir = os.path.abspath(os.path.dirname(yaml_file))
    app_yaml = yaml.load(open(yaml_file))

    sys.stderr.write('static_folder=%s\n' % app_yaml_dir)
    app = Flask(__name__, static_folder=app_yaml_dir)
    
    # static_dir
    # static_files
    # script
    
    # app.send_static_file
    # send_from_directory('/path/to/static/files', filename)
    
    
    def serve_handler(handler, path):
        pattern = handler['url']
        if 'static_files' in handler:
            static_path = re.sub(pattern + '$', handler['static_files'], path)
            return app.send_static_file(static_path)
        if 'static_dir' in handler:
            m = re.match(pattern, path)
            path = path[m.end():]
            sys.stderr.write('Serving %s out of %s\n' % (path, handler['static_dir']))
            return app.send_static_file(handler['static_dir'] + path)
        if 'script' in handler:
            return script_handler(path, request)
    
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        path = '/' + path
        for handler in app_yaml['handlers']:
            pattern = handler['url']
            if 'static_dir' not in handler:
                pattern += '$'
            if re.match(pattern, path):
                sys.stderr.write('Matched %s to %s\n' % (path, pattern))
                return serve_handler(handler, path)
            else:
                sys.stderr.write('No match %s / %s\n' % (path, pattern))
        return "Didn't match any handlers"

    return app

def script_handler(path, req):
    return "Script response for %s" % path


if __name__ == '__main__':
    yaml_file = sys.argv[1]
    app = make_app(yaml_file, script_handler)
    app.run(host='0.0.0.0', debug=True)
