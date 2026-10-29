def filter_tickets(cursor, status, assignee):
    sql = "SELECT id, title FROM tickets WHERE 1=1"
    params = []
    if status:
        sql += " AND status = ?"
        params.append(status)
    if assignee:
        sql += " AND assignee = ?"
        params.append(assignee)
    cursor.execute(sql, params)
    return cursor.fetchall()
