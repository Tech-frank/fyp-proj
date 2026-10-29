def monthly_summary(cursor):
    cursor.execute(
        "SELECT date_trunc('month', created_at) AS month, COUNT(*) "
        + "FROM signups "
        + "GROUP BY 1 ORDER BY 1"
    )
    return cursor.fetchall()
