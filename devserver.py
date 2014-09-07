#!/usr/bin/env python
'''A flask server which serves static files according to AppEngine's app.yaml.

This helps you transition away from AppEngine!
'''

import os
import re
import sys
import yaml
from flask import Flask, send_from_directory, request

def make_app(yaml_file, script_handlers):
    app_yaml_dir = os.path.abspath(os.path.dirname(yaml_file))
    app_yaml = yaml.load(open(yaml_file))

    app = Flask(__name__, static_folder=app_yaml_dir)
    
    def serve_handler(handler, path):
        pattern = handler['url']
        if 'static_files' in handler:
            static_path = re.sub(pattern + '$', handler['static_files'], path)
            return app.send_static_file(static_path)
        if 'static_dir' in handler:
            m = re.match(pattern, path)
            path = path[m.end():]
            return app.send_static_file(handler['static_dir'] + path)
        if 'script' in handler:
            for pattern, handler in script_handlers:
                m = re.match(pattern, path)
                if not m: continue
                return handler(path, request)  # not very similar to WSGI args
    
    
    @app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
    @app.route('/<path:path>', methods=['GET', 'POST'])
    def catch_all(path):
        path = '/' + path
        for handler in app_yaml['handlers']:
            pattern = handler['url']
            if 'static_dir' not in handler:
                pattern += '$'
            if re.match(pattern, path):
                sys.stderr.write('Matched %s to %s\n' % (path, pattern))
                return serve_handler(handler, path)
        return "Didn't match any handlers"

    return app


def script_handler(path, req):
    return "Script response for %s\nquerystring=%r\nform=%r" % (
            path, req.args, req.form)


if __name__ == '__main__':
    yaml_file = sys.argv[1]
    app = make_app(yaml_file, [('.*', script_handler)])
    app.run(host='0.0.0.0', debug=True)
