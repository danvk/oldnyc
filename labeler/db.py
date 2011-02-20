from google.appengine.ext import db


class ImageRecord(db.Model):
  # key = photo_id
  title = db.StringProperty(required=True)
  date = db.StringProperty()
  location = db.StringProperty()
  description = db.StringProperty()
  thumbnail_jpg = db.BlobProperty()


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
