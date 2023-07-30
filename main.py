from fastapi import FastAPI, File, UploadFile, Request
from globant import *
import csv
import codecs
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from reports import *

app = FastAPI()

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile= File(...)):
    csvReader = csv.reader(codecs.iterdecode(file.file, 'utf-8'))
    data = list(csvReader)
    message_l=load_file(data,file.filename)
    return {"filename": file.filename,
            "message": message_l,
            }


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