from __future__ import print_function
import time
import json
from itertools import zip_longest
from gdoctableapppy import gdoctableapp


from common import *
from athlete import Athlete


# def get_table():
#     document = service.documents().get(documentId=DOCUMENT_ID).execute()
#     table = document['body']['content'][2]


def get_sheets_data(service=SHEETS):
    """
    Returns data from Google Sheets source. It gets all rows of
    SHEET_NAME (the default Sheet in a new spreadsheet).
    """
    return (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=SHEETS_FILE_ID, range=SHEET_NAME)
        .execute()
        .get("values")[:]
    )


def extract_athletes_data_from_sheets():
    """
    Returns the athlete data as a list of dicts where each dict
    represents a athlete (a row from the sheet). Keys are the headings
    of the columns and values are the athletes' data in that column.
    """
    sheets_data = get_sheets_data(service=SHEETS)
    headers = sheets_data[0]
    athletes_data = sheets_data[1:]
    athletes_list = []

    for row in athletes_data:
        data = dict(zip(headers, row))
        name = data.pop(STR_NAME)
        athlete = find_athlete(name, athletes_list)
        if athlete is None:
            athletes_list.append(Athlete(name, data))
        else:
            athlete.insert_data(data)

    headers.remove(STR_DATE)
    headers.remove(STR_NAME)

    return headers, athletes_list


def find_athlete(name: str, athletes_list) -> Athlete:
    found_athlete = None
    for athlete in athletes_list:
        if name == athlete.name:
            found_athlete = athlete
            break
    return found_athlete


def copy_template_doc(athlete_name, service=DRIVE):
    """
    Copies letter template document using Drive API then
    returns file ID of (new) copy.
    """
    copy_doc_name = {"name": f"KBBMA Fitness Assessments - {athlete_name}"}
    copy_doc_id = (
        service.files()
        .copy(body=copy_doc_name, fileId=DOCS_FILE_ID, fields="id")
        .execute()
        .get("id")
    )
    return copy_doc_id


# def append_template(copy_doc_id, requests, service=DOCS):
#     """
#     Append a template to google doc.
#     """
#     cdoc = service.openById
#     body = doc.getBody()
#     tmpl_body = service.documents().get(documentId=DOCS_FILE_ID).execute()
#     print(tmpl_body["body"]["content"])
#     requests.append(tmpl_body["body"]["content"])
#     return requests


def replace_variables_in_doc(merge):
    """
    Replaces all instances of each key in merge with its value
    in the Google Doc.
    """
    context = merge.iteritems() if hasattr({}, "iteritems") else merge.items()

    # "search & replace" API requests for mail merge substitutions
    requests = [
        {
            "replaceAllText": {
                "containsText": {
                    "text": f"<{key}>",
                    "matchCase": False,
                },
                "replaceText": value,
            }
        }
        for key, value in context
    ]
    return requests


def create_table_in_doc(athlete, headers, doc_id):
    """
    Add the athlete's data to the table in the Google Doc.
    """
    values = [[""] + headers]

    for data in athlete.data_list:
        values.append(list(data.values()))
    values = list(map(list, zip_longest(*values, fillvalue="")))

    resource = {
        "oauth2": CREDS,
        "documentId": doc_id,
        "tableIndex": 0,
        "values": values,
    }
    gdoctableapp.SetValues(resource)


if __name__ == "__main__":
    headers, athletes_list = extract_athletes_data_from_sheets()
    for athlete in athletes_list:
        copy_doc_id = copy_template_doc(athlete_name=athlete.name)

        requests = []
        requests.append(replace_variables_in_doc(merge={STR_NAME: athlete.name}))
        create_table_in_doc(athlete, headers, copy_doc_id)

        DOCS.documents().batchUpdate(
            documentId=copy_doc_id, body={"requests": requests}
        ).execute()
