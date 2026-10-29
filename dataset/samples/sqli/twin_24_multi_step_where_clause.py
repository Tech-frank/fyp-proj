def report(cursor, start, end, region):
    where = "created BETWEEN %s AND %s"
    params = [start, end]
    if region:
        where = where + " AND region = %s"
        params.append(region)
    query = "SELECT region, SUM(amount) FROM payments WHERE " + where + " GROUP BY region"
    cursor.execute(query, params)
    return cursor.fetchall()
