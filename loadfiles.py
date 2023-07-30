import csv
import codecs
from globant import *

from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, File, UploadFile, Request

app = FastAPI()



@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile= File(...)):
    csvReader = csv.reader(codecs.iterdecode(file.file, 'utf-8'))
    data = list(csvReader)
    message_l=load_file(data,file.filename)
    return {"filename": file.filename,
            "message": message_l,
            }