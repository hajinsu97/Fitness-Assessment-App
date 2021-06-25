import os

from flask_sqlalchemy import SQLAlchemy
import flask
from flask_login import LoginManager
import google_auth_oauthlib.flow

# Flask app setup
app = flask.Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://wstloniawxdylv:1dd908e999a8a07363bcc90cd51a538ccf673428602c281fc7013acf38aab907@ec2-34-233-114-40.compute-1.amazonaws.com:5432/d3rop9tgagamsp"

# DB setup
db = SQLAlchemy(app)

# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)

# Use the client_secret.json file to identify the application requesting
# authorization. The client ID (from that file) and access scopes are required.
flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    "google-credentials.json",
    scopes=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/documents",
        "https://www.googleapis.com/auth/spreadsheets.readonly",
    ],
)
