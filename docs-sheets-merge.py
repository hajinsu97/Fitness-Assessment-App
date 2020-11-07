from __future__ import print_function
import time
import json
from datetime import datetime

from googleapiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools

from common import *


class Student:
    def __init__(self, name, assessment_results):
        self.name = name
        self.all_assessment_results = [assessment_results]

    def add_assessment_results(assessment_results):
        self.all_assessment_results.append(assessment_results)


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

def get_student_data():
    """
    Returns the student data as a list of dicts where each dict
    represents a student (a row from the sheet). Keys are the headings
    of the columns and values are the students' data in that column.
    
    [
        {
            "Student's Name": Jinsu Ha,
            "Timestamp": 09/09/2020,
            "Pushup": 5,
            "Situp": 10,
        },
    ]

    [
        {
            "Student's Name": Jinsu Ha,
            "Results": [
                {
                    "Timestamp": 09/09/2020,
                    "Pushup": 5,
                    "Situp": 10,
                },
                {
                    "Timestamp": 12/09/2020,
                    "Pushup": 9,
                    "Situp": 16,
                },
            ]
        },
    ]
    """
    
    data = get_sheets_data(service=SHEETS)
    headers = data[0]
    student_data = data[1:]

    # Find the index of the students name column
    student_name_index = headers.index(STR_STUDENTS_NAME)
    headers.pop(student_name_index)
    students = []

    # consider ["Jinsu Ha": Student(...), ...] for easier search?

    for student in student_data:
        student_name = student.pop(student_name_index)
        
        if student_name in 
        # Create the assessment_results dict with the remaining data
        assessment_results = dict(zip(headers, student))

        students.append(
            Student(
                name=student_name,
                assessment_results=assessment_results
            )
        )

    return students

def copy_template_doc(student_name, tmpl_id, service=DRIVE):
    """
    Copies letter template document using Drive API then
    returns file ID of (new) copy.
    """
    copy_doc_name = {'name': f'KBBMA Fitness Assessments - {student_name}'}
    copy_doc_id = service.files().copy(body=copy_doc_name, fileId=tmpl_id, fields='id').execute().get('id')
    return copy_doc_id

def append_template(tmpl_id, copy_doc_id, service=DOCS):
    cdoc = service.openById
    body = doc.getBody()
    tmpl_body = service.documents().get(documentId=tmpl_id).execute()
    print(tmpl_body["body"]["content"])
    requests.append(tmpl_body["body"]["content"])
    service.documents().batchUpdate(documentId=copy_doc_id, body={'requests': requests}).execute()

def merge_student_data_to_template_doc(merge, copy_doc_id, service=DOCS):
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
    students = get_student_data()
    for i, student in enumerate(students):
        copy_doc_id = copy_template_doc(
            student_name = student[STR_STUDENTS_NAME],
            tmpl_id=DOCS_FILE_ID,
            service=DRIVE
        )

        merged_doc_id = merge_student_data_to_template_doc(
            merge=student,
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
