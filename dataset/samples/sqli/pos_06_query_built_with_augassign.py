def filter_tickets(cursor, status, assignee):
    sql = "SELECT id, title FROM tickets WHERE 1=1"
    if status:
        sql += " AND status = '" + status + "'"
    if assignee:
        sql += " AND assignee = '" + assignee + "'"
    cursor.execute(sql)
    return cursor.fetchall()
