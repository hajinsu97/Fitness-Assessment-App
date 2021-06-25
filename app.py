# Python standard libraries
import json
import re
import os
import sqlite3

# Third-party libraries
import flask
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build

# Internal imports
from db import init_db_command
from user import User
from fitness_assessment_app import generate_reports

# Flask app setup
app = flask.Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)

# Naive database setup
# try:
#     init_db_command()
# except sqlite3.OperationalError:
#     # Assume it's already been created
#     pass

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

# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


def get_file_id_from_url(url: str) -> str:
    return re.search(
        "https://docs.google.com/(document|spreadsheets)/d/(.*)/edit.*", url
    ).group(2)


def get_doc_url_from_id(doc_id: str) -> str:
    return f"https://docs.google.com/document/d/{doc_id}"


@app.route("/")
def index():
    if current_user.is_authenticated:
        html = (
            "<p>Hello, {}! You're logged in! Email: {}</p>"
            "<div><p>Google Profile Picture:</p>"
            '<img src="{}" alt="Google profile pic"></img></div>'
            '<a class="button" href="/logout">Logout</a>'.format(
                current_user.name, current_user.email, current_user.profile_pic
            )
        )
        doc_url = str(flask.escape(flask.request.args.get("doc_url", "")))
        sheets_url = str(flask.escape(flask.request.args.get("sheets_url", "")))
        sheets_name = str(flask.escape(flask.request.args.get("sheets_name", "")))
        if doc_url and sheets_url and sheets_name:
            doc_id = get_file_id_from_url(doc_url)
            sheets_id = get_file_id_from_url(sheets_url)
            docs = generate_reports(doc_id, sheets_id, sheets_name, flow.credentials)
            for (doc_name, doc_id) in docs:
                html += f'<a href="{get_doc_url_from_id(doc_id)}">{doc_name}</a><br>'
        else:
            # TODO: redirect to a /loading endpoint then /complete endpoint with @login_required
            html += """<form action="" method="get">
                Google Doc URL: <input type="text" name="doc_url"><br>
                Google Sheets URL: <input type="text" name="sheets_url"><br>
                Google Sheets Name: <input type="text" name="sheets_name"><br>
                <input type="submit" value="Generate Reports">
              </form>"""
        return html
    else:
        return '<a class="button" href="/login">Google Login</a>'


@app.route("/login")
def login():
    # Indicate where the API server will redirect the user after the user completes
    # the authorization flow. The redirect URI is required. The value must exactly
    # match one of the authorized redirect URIs for the OAuth 2.0 client, which you
    # configured in the API Console. If this value doesn't match an authorized URI,
    # you will get a 'redirect_uri_mismatch' error.
    flow.redirect_uri = flask.request.base_url + "/callback"

    # Generate URL for request to Google's OAuth 2.0 server.
    # Use kwargs to set optional request parameters.
    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type="offline",
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes="true",
    )

    flask.session["state"] = state
    return flask.redirect(authorization_url)


@app.route("/login/callback")
def callback():
    print(flask.request)
    state = flask.session["state"]
    flow.redirect_uri = flask.url_for("callback", _external=True)

    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store the credentials in the session.
    credentials = flow.credentials
    flask.session["credentials"] = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }

    oauth2_client = build("oauth2", "v2", credentials=credentials)
    user_info = oauth2_client.userinfo().get().execute()

    # Create a user in the db with the information provided by Google
    user = User.get(user_info["id"])

    # Doesn't exist? Add it to the database.
    if not user:
        User.create(
            id_=user_info["id"],
            name=user_info["email"],
            email=user_info["given_name"],
            profile_pic=user_info["picture"],
        )

    # Begin user session by logging the user in
    login_user(user)

    # Send user back to homepage
    return flask.redirect(flask.url_for("index"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return flask.redirect(flask.url_for("index"))


if __name__ == "__main__":
    app.run(ssl_context="adhoc")
