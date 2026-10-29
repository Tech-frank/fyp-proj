import os

import psycopg2


def open_reporting_connection():
    return psycopg2.connect(
        host="reports.db.local",
        dbname="analytics",
        user="report_reader",
        password=os.environ["REPORT_DB_PASSWORD"],
    )
