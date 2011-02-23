from google.appengine.ext import db


class ImageRecord(db.Model):
  # key = seq_id (it's convenient to have it both as a key and a field)
  seq_id = db.IntegerProperty()  # assigned sequentially, starting with 0.
  photo_id = db.StringProperty()
  title = db.StringProperty()
  date = db.StringProperty()
  location = db.StringProperty()
  description = db.TextProperty()
  photo_url = db.StringProperty()
  image = db.BlobProperty()


class User(db.Model):
  # key = user_id = cookie
  name = db.StringProperty()  # optional
  first_use = db.DateTimeProperty(auto_now_add=True)
  num_seen = db.IntegerProperty()


class Geocode(db.Model):
  user = db.ReferenceProperty(User)
  photo = db.ReferenceProperty(ImageRecord)
  geocode_date = db.DateTimeProperty(auto_now_add=True)

  feasibility = db.StringProperty(choices=set([
    "yes",    # this record includes a geocode
    "no",     # image cannot be geocoded
    "maybe",  # image can be geocoded, but not by me.
    "notsf"   # image is not in San Francisco
  ]))
  location = db.GeoPtProperty()
  orientation = db.IntegerProperty()  # 0-360, 0=E, 90=N, ...

  setting = db.StringProperty(choices=set(['indoors', 'outdoors']))
  rating = db.IntegerProperty()
  comments = db.TextProperty()
