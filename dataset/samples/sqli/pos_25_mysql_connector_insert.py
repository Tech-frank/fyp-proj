import mysql.connector


def log_visit(conn: mysql.connector.MySQLConnection, page, referrer):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO visits (page, referrer) VALUES ('%s', '%s')" % (page, referrer))
    conn.commit()
