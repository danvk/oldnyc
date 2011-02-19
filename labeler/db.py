from google.appengine.ext import db

class ImageRecordModel(db.Model):
  # key = photo_id
  title = db.StringProperty(required=True)
  date = db.StringProperty()
  location = db.StringProperty()
  description = db.StringProperty()
  thumbnail_jpg = db.BlobProperty()

class UserModel(db.Model):
  # key = user_id = cookie
  name = db.StringProperty()  # optional

class GeocodeModel(db.Model):
  user = db.ForeignKey(UserModel)
  photo_id = db.ForeignKey(ImageRecordModel)
  feasibility = db.StringProperty(required=True, choices=set([
    "yes",    # this record includes a geocode
    "no",     # image cannot be geocoded
    "maybe"]) # image can be geocoded, but not by me.
  location = db.GeoPtProperty()
  orientation = db.IntegerProperty()  # 0-360, 0=E, 90=N, ...
