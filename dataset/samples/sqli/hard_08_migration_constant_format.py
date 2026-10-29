COLUMN = "last_login"
DEFAULT = "NULL"


def add_column(cursor):
    sql = "ALTER TABLE users ADD COLUMN {} TIMESTAMP DEFAULT {}".format(COLUMN, DEFAULT)
    cursor.execute(sql)
