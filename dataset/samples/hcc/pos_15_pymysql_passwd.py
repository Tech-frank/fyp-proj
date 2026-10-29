import pymysql

conn = pymysql.connect(
    host="127.0.0.1",
    user="legacy_app",
    passwd="L3gacy_Db_2019!",
    db="crm",
    charset="utf8mb4",
)
