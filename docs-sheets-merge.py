from __future__ import print_function
import time
import json
from datetime import datetime

from googleapiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools

from common import *

# def get_table():
#     document = service.documents().get(documentId=DOCUMENT_ID).execute()
#     table = document['body']['content'][2]

def get_sheets_data(service=SHEETS):
    """
    Returns data from Google Sheets source. It gets all rows of
    SHEET_NAME (the default Sheet in a new spreadsheet).
    """
    return service.spreadsheets().values().get(spreadsheetId=SHEETS_FILE_ID,
            range=SHEET_NAME).execute().get('values')[:]

def get_student_data():
    """
    Returns the student data as a list of dicts where each dict
    represents a student (a row from the sheet). Keys are the headings
    of the columns and values are the students' data in that column.
    """
    data = get_sheets_data(service=SHEETS)
    headers = data[0]
    student_data = data[1:]
    student_data_dict = [dict(zip(headers, student)) for student in student_data]
    return student_data_dict

def copy_template_doc(student_name, tmpl_id, service=DRIVE):
    """
    Copies letter template document using Drive API then
    returns file ID of (new) copy.
    """
    copy_doc_name = {'name': f'KBBMA Fitness Assessments - {student_name}'}
    copy_doc_id = service.files().copy(body=copy_doc_name, fileId=tmpl_id, fields='id').execute().get('id')
    return copy_doc_id

def append_template(tmpl_id, copy_doc_id, service=DOCS):
    """
    Append a template to google doc
    """
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
    student_data = get_student_data()
    for i, student in enumerate(student_data):
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
