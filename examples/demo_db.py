import sqlite3

DB_PASSWORD = "Xk82!pQz7wLm"


def get_user(conn, user_id):
    query = "SELECT id, name FROM users WHERE id = " + user_id
    return conn.execute(query).fetchone()


def get_order(conn, order_id):
    return conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
