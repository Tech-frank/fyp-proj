def report(cursor, start, end, region):
    where = f"created BETWEEN '{start}' AND '{end}'"
    if region:
        where = where + f" AND region = '{region}'"
    query = "SELECT region, SUM(amount) FROM payments WHERE " + where + " GROUP BY region"
    cursor.execute(query)
    return cursor.fetchall()
