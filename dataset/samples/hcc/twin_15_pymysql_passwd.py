import os

import pymysql

conn = pymysql.connect(
    host="127.0.0.1",
    user="legacy_app",
    passwd=os.environ["CRM_DB_PASSWD"],
    db="crm",
    charset="utf8mb4",
)
