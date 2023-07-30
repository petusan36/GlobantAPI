from globant import *
from tabulate import tabulate

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

def tabulated_rows(table_headers,table_data):
    return tabulate(table_data, headers= table_headers, tablefmt='html', colalign=("right",))

def reports(report):
    db_path=r"/home/pedro/Documentos/gitRepositorios/GlobantAPI/globant.db"
    query_select=queries_reports(report)
    db_connection=create_connection(db_path)
    cur = db_connection.cursor()
    cur.execute(query_select)
    headers=tuple([member[0] for member in cur.description])
    rows = cur.fetchall()
    return tabulated_rows(headers,rows)
