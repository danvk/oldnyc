from google.appengine.ext import db


class ImageRecord(db.Model):
  # key = seq_id (it's convenient to have it both as a key and a field)
  seq_id = db.IntegerProperty()  # assigned sequentially, starting with 0.
  photo_id = db.StringProperty()
  title = db.StringProperty()
  date = db.StringProperty()
  location = db.StringProperty()
  description = db.StringProperty()
  photo_url = db.StringProperty()
  image = db.BlobProperty()


class User(db.Model):
  # key = user_id = cookie
  name = db.StringProperty()  # optional
  first_use = db.DateTimeProperty(auto_now_add=True)


class Geocode(db.Model):
  user = db.ReferenceProperty(User)
  photo_id = db.ReferenceProperty(ImageRecord)
  feasibility = db.StringProperty(required=True, choices=set([
    "yes",    # this record includes a geocode
    "no",     # image cannot be geocoded
    "maybe"]  # image can be geocoded, but not by me.
  ))
  location = db.GeoPtProperty()
  orientation = db.IntegerProperty()  # 0-360, 0=E, 90=N, ...
  date = db.DateTimeProperty(auto_now_add=True)
