import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Headers in Athlete data
STR_NAME = "Name"
STR_DATE = "Date"

# Authorization constants
CLIENT_SECRETS_FILE = "google-credentials.json"
SCOPES = (  # iterable or space-delimited string
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
)


def get_credentials():
    """
    Uses project credentials in CLIENT_SECRETS_FILE along with requested OAuth2
    scopes for authorization, and caches API tokens in TOKEN_STORE_FILE.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds


# Service endpoints to Google APIs
CREDS = get_credentials()
DRIVE = build("drive", "v3", credentials=CREDS)
DOCS = build("docs", "v1", credentials=CREDS)
SHEETS = build("sheets", "v4", credentials=CREDS)
