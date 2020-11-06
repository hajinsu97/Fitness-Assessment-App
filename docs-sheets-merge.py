from __future__ import print_function
import time
import json
from datetime import datetime

from googleapiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools

# Fill-in IDs of your Docs template & any Sheets data source
DOCS_FILE_ID = '1JfYsCbmk1uTGrgC15OFubSjPbbD0hopqv4d0xwOyzOM'
SHEETS_FILE_ID = '1yJ7IM1NaNHq2xm7zPgHrV6lcidHhB5_gtVEUx-D7mm8'
SHEET_NAME = 'Fitness Tests Data'

# authorization constants
CLIENT_ID_FILE = 'credentials.json'
TOKEN_STORE_FILE = 'token.json'
SCOPES = (  # iterable or space-delimited string
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/spreadsheets.readonly',
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

# service endpoints to Google APIs
HTTP = get_http_client()
DRIVE = discovery.build('drive', 'v3', http=HTTP)
DOCS = discovery.build('docs', 'v1', http=HTTP)
SHEETS = discovery.build('sheets', 'v4', http=HTTP)

def get_sheets_data(service=SHEETS):
    """
    Returns data from Google Sheets source. It gets all rows of
    SHEET_NAME (the default Sheet in a new spreadsheet).
    """
    return service.spreadsheets().values().get(spreadsheetId=SHEETS_FILE_ID,
            range=SHEET_NAME).execute().get('values')[:]

def get_table():
    document = service.documents().get(documentId=DOCUMENT_ID).execute()
    table = document['body']['content'][2]

def copy_template(tmpl_id, service=DRIVE):
    """
    Copies letter template document using Drive API then
    returns file ID of (new) copy.
    """
    doc_creation_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    copy_doc_name = {'name': f'KBBMA Fitness Assessments {doc_creation_time}'}
    copy_doc_id = service.files().copy(body=copy_doc_name, fileId=tmpl_id, fields='id').execute().get('id')
    return copy_doc_id

def append_template(tmpl_id, copy_doc_id, service=DOCS):
    cdoc = service.openById
    body = doc.getBody()
    tmpl_body = service.documents().get(documentId=tmpl_id).execute()
    print(tmpl_body["body"]["content"])
    requests.append(tmpl_body["body"]["content"])
    service.documents().batchUpdate(documentId=copy_doc_id, body={'requests': requests}).execute()

def merge_template(merge, copy_doc_id, service=DOCS):
    """
    Copies template document and merges data into newly-minted copy then
    returns its file ID.
    """
    context = merge.iteritems() if hasattr({}, 'iteritems') else merge.items()

    # "search & replace" API requests for mail merge substitutions
    requests = [{'replaceAllText': {
                'containsText': {
                    'text': f'<{key}>' ,
                    'matchCase': False,
                },
                'replaceText': value,
            }} for key, value in context]
    # send requests to Docs API to do actual merge
    service.documents().batchUpdate(body={'requests': requests},
            documentId=copy_doc_id, fields='').execute()
    return copy_doc_id


if __name__ == '__main__':
    # get row data, then loop through & process each form letter
    data = get_sheets_data(service=SHEETS)
    headers = data[0]
    student_data = data[1:]
    for i, row in enumerate(student_data):
        copy_doc_id = copy_template(
            tmpl_id=DOCS_FILE_ID,
            service=DRIVE
        )

        merge = dict(zip(headers, row))
        merged_doc_id = merge_template(
            merge=merge,
            copy_doc_id=copy_doc_id,
            service=DOCS
        )
        # # if theres more students to create an assessment for
        # if i < len(student_data) - 1: # and next row is not the same student
        #     append_template(
        #         tmpl_id=DOCS_FILE_ID,
        #         copy_doc_id=copy_doc_id,
        #         service=DOCS
        #     )
        print(f'Merged letter {i+1}: docs.google.com/document/d/{merged_doc_id}/edit')
