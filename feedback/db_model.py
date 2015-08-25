from google.appengine.ext import db

class MyModel(db.Model):
	property1 = db.StringProperty()
	property2 = db.DateTimeProperty()
	property3 = db.IntegerProperty() 


class UserFeedback(db.Model):
    photo_id = db.StringProperty()
    feedback = db.TextProperty()
    user_ip = db.StringProperty()
    cookie = db.StringProperty()
    datetime = db.DateTimeProperty(auto_now_add=True)
    user_agent = db.TextProperty()
    location = db.TextProperty()
    origin = db.StringProperty()
