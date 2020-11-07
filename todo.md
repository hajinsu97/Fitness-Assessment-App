# TO DO
Featurees
- In the table, each column by month
- 1 sheet has all the data but columns filtered by date

Next update:
 - one doc each page by student name
 - Score based on average - Colour box to indicate NI, Above Avg, Avg, etc.
 - Python app to auto add new active students and cleanup inactive students
 - Create one google doc with line breaks
    - Copy the template with a page break each time
    - replace the values after copying template
- Autoformat timestamp in google sheets
- Sort data by name and if name is different create a page break and start a new page
    - remove training whitespace and check if name is same with .no case
- optimize get_student_data generating dictionary, searching student, consider making an object (is this more efficient?)
- better comments
- type hinting
- unit tests




doc_creation_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')