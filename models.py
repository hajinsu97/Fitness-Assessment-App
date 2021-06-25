from flask_login import UserMixin
from config import db

# Models
class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Numeric(), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    profile_pic = db.Column(db.String(100))

    def __init__(self, id, name, email, profile_pic):
        self.id = id
        self.name = name
        self.email = email
        self.profile_pic = profile_pic
        create_user(self)


# User REST API
def create_user(user):
    # Add user to the database
    db.session.add(user)
    db.session.commit()
