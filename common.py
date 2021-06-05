from googleapiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools

# Fill-in IDs of your Docs template & any Sheets data source
DOCS_FILE_ID = "1JfYsCbmk1uTGrgC15OFubSjPbbD0hopqv4d0xwOyzOM"
SHEETS_FILE_ID = "1yJ7IM1NaNHq2xm7zPgHrV6lcidHhB5_gtVEUx-D7mm8"
SHEET_NAME = "Fitness Tests Data"

# Headers in Student data
STR_STUDENTS_NAME = "Student's Name"
STR_DATE = "Date"

# Authorization constants
CLIENT_ID_FILE = "credentials.json"
TOKEN_STORE_FILE = "token.json"
SCOPES = (  # iterable or space-delimited string
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
)


def get_http_client():
    """Uses project credentials in CLIENT_ID_FILE along with requested OAuth2
    scopes for authorization, and caches API tokens in TOKEN_STORE_FILE.
    """
    store = file.Storage(TOKEN_STORE_FILE)
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_ID_FILE, SCOPES)
        creds = tools.run_flow(flow, store)
    return creds.authorize(Http())


# Service endpoints to Google APIs
HTTP = get_http_client()
DRIVE = discovery.build("drive", "v3", http=HTTP)
DOCS = discovery.build("docs", "v1", http=HTTP)
SHEETS = discovery.build("sheets", "v4", http=HTTP)
