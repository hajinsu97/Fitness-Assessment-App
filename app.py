# Python standard libraries
import re

# Third-party libraries
from flask import request, url_for, escape, render_template, session, redirect
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user,
)
import google.oauth2.credentials
from googleapiclient.discovery import build

# Internal imports
from config import *
from models import *
from fitness_assessment_app import generate_reports

# Use the client_secret.json file to identify the application requesting
# authorization. The client ID (from that file) and access scopes are required.
flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    CLIENT_SECRETS_FILE, scopes=SCOPES
)

# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


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
        doc_url = str(escape(request.args.get("doc_url", "")))
        sheets_url = str(escape(request.args.get("sheets_url", "")))
        sheets_name = str(escape(request.args.get("sheets_name", "")))
        if doc_url and sheets_url and sheets_name:
            doc_id = get_file_id_from_url(doc_url)
            sheets_id = get_file_id_from_url(sheets_url)
            docs = generate_reports(doc_id, sheets_id, sheets_name, flow.credentials)
            for (doc_name, doc_id) in docs:
                html += f'<a href="{get_doc_url_from_id(doc_id)}">{doc_name}</a><br>'
        else:
            # TODO: redirect to a /loading endpoint then /complete endpoint with @login_required
            html += """<form action="" method="get">
                1) Create a folder in your Google Drive named "Fitness Assessments"<br>
                <p>2) Copy the <a href="https://docs.google.com/document/d/1JfYsCbmk1uTGrgC15OFubSjPbbD0hopqv4d0xwOyzOM/edit?usp=sharing" target="_blank" rel="noopener noreferrer">Fitness Assessment Document Template </a> to the folder your just created and enter it's URL below.<br>Google Doc URL: <input type="text" name="doc_url"></p>
                <p>3) Copy the <a href="https://docs.google.com/spreadsheets/d/1yJ7IM1NaNHq2xm7zPgHrV6lcidHhB5_gtVEUx-D7mm8/edit?usp=sharing" target="_blank" rel="noopener noreferrer">Fitness Tests Sheets Template</a> to the folder your just created and enter it's URL below.<br> Google Sheets URL: <input type="text" name="sheets_url"></p>
                4) Enter the name of the sheet to generate reports for (e.g., Sheet1).<br>
                Google Sheets Name: <input type="text" name="sheets_name"><br>
                <input type="submit" value="Generate Reports">
              </form>"""
        return html
    else:
        return render_template("login.html")


@app.route("/login")
def login():
    # Indicate where the API server will redirect the user after the user completes
    # the authorization flow. The redirect URI is required. The value must exactly
    # match one of the authorized redirect URIs for the OAuth 2.0 client, which you
    # configured in the API Console. If this value doesn't match an authorized URI,
    # you will get a 'redirect_uri_mismatch' error.
    flow.redirect_uri = request.base_url + "/callback"

    # Generate URL for request to Google's OAuth 2.0 server.
    # Use kwargs to set optional request parameters.
    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type="offline",
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes="true",
    )

    session["state"] = state
    return redirect(authorization_url)


@app.route("/login/callback")
def callback():
    # Use the client_secret.json file and the state from the authorization_url
    # to identify the application requesting authorization.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=session["state"]
    )

    flow.redirect_uri = url_for("callback", _external=True)

    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store the credentials in the session.
    credentials = flow.credentials
    session["credentials"] = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }

    oauth2_client = build("oauth2", "v2", credentials=credentials)
    user_info = oauth2_client.userinfo().get().execute()

    # Doesn't exist? Add it to the database.
    user = User.query.filter_by(id=user_info["id"]).first()
    if not user:
        user = User(
            id=user_info["id"],
            name=user_info["given_name"],
            email=user_info["email"],
            profile_pic=user_info["picture"],
        )

    # Begin user session by logging the user in
    login_user(user)

    # Send user back to homepage
    return redirect(url_for("index"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(ssl_context="adhoc")
