def big_spenders(cursor, minimum):
    cursor.execute(
        "SELECT customer_id, SUM(total) AS spent FROM orders "
        "GROUP BY customer_id HAVING SUM(total) > {}".format(minimum)
    )
    return cursor.fetchall()
