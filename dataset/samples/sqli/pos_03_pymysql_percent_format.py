def orders_for_customer(conn, customer_email):
    with conn.cursor() as cur:
        cur.execute("SELECT id, total FROM orders WHERE email = '%s'" % customer_email)
        return cur.fetchall()
