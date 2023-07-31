-- sqlite3 globant.db
CREATE TABLE IF NOT EXISTS departments (
	id INTEGER PRIMARY KEY,
	department TEXT
) WITHOUT ROWID;


CREATE TABLE IF NOT EXISTS jobs (
	id INTEGER PRIMARY KEY,
	job TEXT
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS hired_employees (
	id INTEGER PRIMARY KEY,
	name TEXT,
	datetime TEXT,
	department_id INTEGER,
	job_id INTEGER,
	FOREIGN KEY (department_id) REFERENCES "departments" (id)
		ON DELETE NO ACTION ON UPDATE NO ACTION
	FOREIGN KEY (job_id) REFERENCES "jobs" (id)
		ON DELETE NO ACTION ON UPDATE NO ACTION
) WITHOUT ROWID;


SELECT d.department, j.job, count(1)  FROM hired_employees AS he
INNER JOIN departments AS d ON he.department_id = d.id
INNER JOIN jobs AS j ON he.job_id = j.id
WHERE strftime('%Y', he.datetime) = '2021'
GROUP BY d.department, j.job limit 10;