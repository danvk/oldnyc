from google.appengine.api import memcache

from datetime import datetime
import random
import logging

import db

def randomImage(user):
  """user is a db.User entry. Returns an integer image ID."""
  # Use memcache to avoid computing max_id repeatedly.
  max_id = memcache.get('max_id')
  if not max_id:
    qs = db.ImageRecord.all().order('-seq_id').fetch(limit=1)
    assert len(qs) == 1
    max_id = qs[0].seq_id
    memcache.set('max_id', max_id, 3600)

  # We generate an ordering of IDs for the user and walk through it.
  r = random.Random(str(user.key()))
  ids = range(0, 1 + max_id)
  r.shuffle(ids)
  num_seen = user.num_seen or 0
  id = ids[num_seen % (1 + max_id)]
  user.num_seen = 1 + num_seen
  user.put()
  return id

def userFromCookie(handler):
  """handler is a webapp.RequestHandler. Returns the db.user entry."""
  cookie = None
  if 'id' in handler.request.cookies:
    cookie = handler.request.cookies['id']

  user = None
  if not cookie:
    # Create a new entry for this user and set their cookie.
    user = db.User()
    user.put()
    handler.response.headers.add_header(
      'Set-Cookie',
      'id=%s' % user.key(),
      Expires='Wed, 13-Jan-2021 22:23:01 GMT')

  else:
    # Get their record.
    user = db.User.get(cookie)
    assert user

  return user
