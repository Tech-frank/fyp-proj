import sqlite3


def count_rows(db_path, table):
    conn = sqlite3.connect(db_path)
    total = conn.execute("SELECT COUNT(*) FROM " + table).fetchone()[0]
    conn.close()
    return total
