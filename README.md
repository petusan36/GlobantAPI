
# GlobantAPI

GlobantAPI is a Python app made  on FastApi library to load files to migrate from a database and generate two reports needed for users.
```
app
│ __init__.py  
│ globant.py    
│ loadfiles.py
│ main.py
│ reports.py
└─folder1
archivos
│ CREATE_globant.sql
│ deparments.csv
│ hired_employees.csv
│ jobs.csv
│ reports.csv
Dockerfile
LICENSE
README.md
requirements.txt
```
***app*** folder: contain all files with application logic
***archivos*** folder: Have all files to complement or used to create tables or load data into database.

## Installation

For this app you must use [docker](https://docs.docker.com/get-docker/) to install GlobantAPI.

First you must be in main directory and execute ***Dockerfile*** that it'll build an image with name  with next command.
```docker
docker build -t globantapi .
```
>The name used for the image is ***globantapi*** but you can change it with other one you want.

After that, the image is ready for be launched. To check if the image exists you can execute ``docker images`` and watch if ***globantapi*** is in the list.

Next step is run the builded image, to do that, you must execute the next command for up a container.
```docker
docker run -d --name apig -p 80:80 globantapi
```
>The container name used is ***apig***  but you can change it for any other you want.
You can check if container 

To check if container is up you can execute the next command ``docker ps`` and watch if ``apig`` is running
>To stop the running  container you enter into this one with ``docker exec -it apig bash`` and run kill command to force it to stop ``kill 1`` sending a signal with ``1`` value.

to delete definitly the container and image created you can execute next commands
```docker
docker remove apig
docker image remove globantapi:latest
```



## Usage

Dockerfile
```dockerfile
# Base image.
FROM python:3.9 

# Update linux base.
RUN apt-get update 

# Work directory.
WORKDIR /app
COPY ./app ./ 

# Install sqlite library.
RUN apt-get install -y sqlite3 libsqlite3-dev

# Create DB and tables for API load
RUN sqlite3 -batch globant.db "CREATE TABLE IF NOT EXISTS departments ( \
	id INTEGER PRIMARY KEY, \
	department TEXT \
) WITHOUT ROWID; \
CREATE TABLE IF NOT EXISTS jobs ( \
	id INTEGER PRIMARY KEY, \
	job TEXT \
) WITHOUT ROWID; \
CREATE TABLE IF NOT EXISTS hired_employees ( \
	id INTEGER PRIMARY KEY, \
	name TEXT, \
	datetime TEXT, \
	department_id INTEGER, \
	job_id INTEGER, \
	FOREIGN KEY (department_id) REFERENCES departments (id) \
		ON DELETE NO ACTION ON UPDATE NO ACTION \
	FOREIGN KEY (job_id) REFERENCES jobs (id) \
		ON DELETE NO ACTION ON UPDATE NO ACTION \
) WITHOUT ROWID;"

# Requirements needed for run python.
COPY requirements.txt ./

# Execute requirements for app.
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

# Run command to up uvicorn server on localhost by  port 80.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
```
main.py
```python
from fastapi import FastAPI, File, UploadFile, Request
from globant import *
import csv
import codecs
from fastapi.responses import HTMLResponse
from reports import *

app = FastAPI()

# API Load.
@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile= File(...)):
    csvReader = csv.reader(codecs.iterdecode(file.file, 'utf-8'))
    data = list(csvReader)
    message_l=load_file(data,file.filename)
    return {"filename": file.filename,
            "message": message_l,
            }

# API Report Employees hired in 2021.
@app.get("/employees_hired_2021", response_class=HTMLResponse)
async def employees_hired_2021(request: Request):
    employees_hired_2021=reports("employees_hired_2021")
    html_content = """
    <html><head><style>table, th, td {  padding: 5px; border: solid 1px #777;}
    th { background-color: lightblue; }
    table {  border-collapse: collapse;}</style>
    <title>Reports</title></head>
        <h1>Hired Employees in departments by quartes in 2021</h1>
        <body style="padding: 30px">"""+str(employees_hired_2021)+"""</body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200) 

# API Report Employees hired over mean in departments.
@app.get("/employees_hired_over_mean", response_class=HTMLResponse)
async def employees_hired_over_mean(request: Request):
    employees_hired_over_mean=reports("employees_hired_over_mean")
    html_content = """
    <html><head><style>table, th, td {  padding: 5px; border: solid 1px #777;}
    th { background-color: lightblue; }
    table {  border-collapse: collapse;}</style>
    <title>Reports</title></head>
        <h1>Number of hired employees over mean </h1>
        <body style="padding: 30px">"""+str(employees_hired_over_mean)+"""</body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200) 
```
globant.py
```python
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse
import sqlite3
from sqlite3 import Error as error_db
import os

# Create DB connetion to load and query.
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except error_db as e:
        return e

# Query to insert data for tables in DB.
def insert_data(db_path, data, file_to_db):
    insert_tables = {"departments.csv":"INSERT INTO departments(id,department) values (?,?)",
                     "hired_employees.csv":"INSERT INTO hired_employees(id,name,datetime,department_id,job_id) values (?,?,?,?,?)",
                     "jobs.csv":"INSERT INTO jobs(id,job) values (?,?)"
                    }
    query_insert=insert_tables[file_to_db]
    try:
        db_connection=create_connection(db_path)
        insert_cursor = db_connection.cursor()
        for row in data:
            insert_cursor.execute(query_insert, row)
        db_connection.commit()
        db_connection.close()
        message=f"El archivo {file_to_db} fue insertado".format(file_to_db=file_to_db)
        return message
    except error_db as e:
        return e

# Load files.
def load_file(data, file_to_db):
    try:
        root_path = os.getcwd()
        db_path= root_path+"/globant.db"
        message=insert_data(db_path, data, file_to_db)
        return message
    except error_db as e:
        return e
```
report.py
```python
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse
from globant import *
from tabulate import tabulate

# Report queries.
def queries_reports(query_consult):
    employees_hired_2021 ="""WITH quarters AS(
SELECT
    d.department, j.job, 
    CASE 
        WHEN 0 + strftime('%m', he.datetime) BETWEEN  1 AND  3 THEN 'Q1'
        WHEN 0 + strftime('%m', he.datetime) BETWEEN  4 AND  6 THEN 'Q2'
        WHEN 0 + strftime('%m', he.datetime) BETWEEN  7 AND  9 THEN 'Q3'
        WHEN 0 + strftime('%m', he.datetime) BETWEEN 10 AND 12 THEN 'Q4'
    END AS quarter
FROM hired_employees AS he
INNER JOIN departments AS d ON he.department_id = d.id
INNER JOIN jobs AS j ON he.job_id = j.id
WHERE strftime('%Y', he.datetime) = '2021'
),
qs_grouped AS(
SELECT department,job,
COUNT(quarter) FILTER (WHERE quarter = 'Q1') AS Q1,
COUNT(quarter) FILTER (WHERE quarter = 'Q2') AS Q2,
COUNT(quarter) FILTER (WHERE quarter = 'Q3') AS Q3,
COUNT(quarter) FILTER (WHERE quarter = 'Q4') AS Q4
FROM quarters
GROUP BY department,job,quarter
)
SELECT department,job, 
SUM(Q1) AS Q1, 
SUM(Q2) AS Q2, 
SUM(Q3) AS Q3, 
SUM(Q4) AS Q4
FROM qs_grouped
GROUP BY department,job 
ORDER BY  department ASC,job ASC;"""


    employees_hired_over_mean ="""WITH means AS(
SELECT d.id, d.department, COUNT(he.id) AS conteo
FROM hired_employees AS he
INNER JOIN departments AS d ON he.department_id = d.id
GROUP BY d.id, d.department
),
he_mean_depts AS (
SELECT AVG(conteo) as means_depts FROM means
)
SELECT id, department, conteo AS hired 
FROM means 
WHERE conteo > (SELECT means_depts FROM he_mean_depts)
ORDER BY 3 DESC;"""

    if query_consult == "employees_hired_2021":
        return employees_hired_2021
    elif query_consult == "employees_hired_over_mean":
        return employees_hired_over_mean

# To return tabulated data in HTML format.
def tabulated_rows(table_headers,table_data):
    return tabulate(table_data, headers= table_headers, tablefmt='html', colalign=("right",))

# Call to execute queries.
def reports(report):
    root_path = os.getcwd()
    db_path=root_path+"/globant.db"
    query_select=queries_reports(report)
    db_connection=create_connection(db_path)
    cur = db_connection.cursor()
    cur.execute(query_select)
    headers=tuple([member[0] for member in cur.description])
    rows = cur.fetchall()
    return tabulated_rows(headers,rows)
```
## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
