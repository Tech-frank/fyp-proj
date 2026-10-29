import sqlite3

KNOWN_TABLES = {"users", "orders", "products"}


def count_rows(db_path, table):
    if table not in KNOWN_TABLES:
        raise ValueError(f"unknown table: {table}")
    conn = sqlite3.connect(db_path)
    total = conn.execute("SELECT COUNT(*) FROM " + table).fetchone()[0]
    conn.close()
    return total
