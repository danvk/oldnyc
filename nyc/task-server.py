#!/usr/bin/python
'''
An HTTP server which reads in a task list and then serves up tasks, one per
request. Handy for distributing tasks across a few processes.
'''

import fileinput
import sys
import time
import BaseHTTPServer
import socket
import Queue


HOST_NAME = socket.gethostname()
PORT_NUMBER = 8765

tasklist = Queue.Queue()

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
  def do_GET(s):
    """Respond to a GET request."""
    global tasklist
    if not tasklist.empty():
      s.send_response(200)
      s.send_header("Content-type", "text/plain")
      s.end_headers()
      s.wfile.write(tasklist.get())
    else:
      s.send_response(404)
      s.end_headers()


def keep_running():
  global tasklist
  return not tasklist.empty()


if __name__ == '__main__':
  for x in fileinput.input():
    tasklist.put(x)

  server_class = BaseHTTPServer.HTTPServer
  httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
  try:
    print 'Serving on %s:%d' % (HOST_NAME, PORT_NUMBER)
    while keep_running():
      httpd.handle_request()
  except KeyboardInterrupt:
    pass
  httpd.server_close()
