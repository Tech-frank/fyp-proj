def find_order(cursor, ref):
    cursor.execute("SELECT * FROM orders WHERE ref = %s", (ref,))
    return cursor.fetchone()
