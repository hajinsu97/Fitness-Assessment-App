from flask import Flask
from flask import request, escape
from fitness_assessment_app import generate_reports

app = Flask(__name__)


@app.route("/")
def index():
    doc_url = str(escape(request.args.get("doc_url", "")))
    sheets_url = str(escape(request.args.get("sheets_url", "")))
    sheets_name = str(escape(request.args.get("sheets_name", "")))
    if doc_url and sheets_url and sheets_name:
        docs = generate_reports(doc_url, sheets_url, sheets_name)
        html = ""
        for (doc_name, doc_id) in docs:
            doc_url = f"https://docs.google.com/document/d/{doc_id}"
            html += f'<a href="{doc_url}">{doc_name}</a>'
        return html
    return """<form action="" method="get">
                Google Doc URL: <input type="text" name="doc_url">
                Google Sheets URL: <input type="text" name="sheets_url">
                Google Sheets Name: <input type="text" name="sheets_name">
                <input type="submit" value="Generate Reports">
              </form>"""


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
