FROM python:3.9 

RUN apt-get update 

# 
WORKDIR /app
COPY ./app ./ 

RUN apt-get install -y sqlite3 libsqlite3-dev


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

# 
COPY requirements.txt ./

# 
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

# 
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]