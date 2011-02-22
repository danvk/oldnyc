from datetime import datetime
import random
import logging

import db

def randomImage(user):
  """user is a db.User entry. Returns an integer image ID."""
  qs = db.ImageRecord.all().order('-seq_id').fetch(limit=1)
  assert len(qs) == 1
  max_id = qs[0].seq_id
  # We use a combination of user id and time as the random number seed.
  # TODO(danvk): surely there is a better way to do this.
  r = random.Random(str(user.key()) + datetime.now().isoformat())
  id = r.randint(0, max_id)
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
