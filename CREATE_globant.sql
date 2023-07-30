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


--Number of employees hired for each job and department in 2021 divided by quarter. The table must be ordered alphabetically by department and job.
WITH quarters AS(
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
ORDER BY  department ASC,job ASC;

-- List of ids, name and number of employees hired of each department that hired more employees than the mean of employees hired in 2021 for all the departments, ordered by the number of employees hired (descending).

WITH means AS(
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
ORDER BY 3 DESC;





