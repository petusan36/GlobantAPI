from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse
import sqlite3
from sqlite3 import Error as error_db
import os


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except error_db as e:
        return e

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


def load_file(data, file_to_db):
    try:
        root_path = os.getcwd()
        db_path= root_path+"/globant.db"
        message=insert_data(db_path, data, file_to_db)
        return message
    except error_db as e:
        return e