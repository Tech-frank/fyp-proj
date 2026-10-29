TABLES = ["users", "orders", "payments"]


def truncate_all(conn):
    cur = conn.cursor()
    for table in TABLES:
        cur.execute(f"TRUNCATE TABLE {table} CASCADE")
    conn.commit()
