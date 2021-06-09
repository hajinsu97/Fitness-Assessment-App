from flask import Flask
from flask import request, escape
from flask.globals import g
from fitness_assessment_app import generate_reports
import re

app = Flask(__name__)


def get_file_id_from_url(url: str) -> str:
    return re.search(
        "https://docs.google.com/(document|spreadsheets)/d/(.*)/edit.*", url
    ).group(2)


def get_doc_url_from_id(doc_id: str) -> str:
    return f"https://docs.google.com/document/d/{doc_id}"


@app.route("/")
def index():
    doc_url = str(escape(request.args.get("doc_url", "")))
    sheets_url = str(escape(request.args.get("sheets_url", "")))
    sheets_name = str(escape(request.args.get("sheets_name", "")))
    if doc_url and sheets_url and sheets_name:
        doc_id = get_file_id_from_url(doc_url)
        sheets_id = get_file_id_from_url(sheets_url)
        docs = generate_reports(doc_id, sheets_id, sheets_name)
        html = ""
        for (doc_name, doc_id) in docs:
            html += f'<a href="{get_doc_url_from_id(doc_id)}">{doc_name}</a><br>'
        return html
    return """<form action="" method="get">
                Google Doc URL: <input type="text" name="doc_url"><br>
                Google Sheets URL: <input type="text" name="sheets_url"><br>
                Google Sheets Name: <input type="text" name="sheets_name"><br>
                <input type="submit" value="Generate Reports">
              </form>"""


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
