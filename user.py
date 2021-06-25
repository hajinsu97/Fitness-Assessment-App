from flask_login import UserMixin
from config import db

# Models
class User(UserMixin, db.Model):
    __tablename__ = "user"

    _id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    profile_pic = db.Column(db.String(100))


# User REST API
def create_user(user):
    # Add user to the database
    db.session.add(user)
    db.session.commit()
