FILTERABLE = ("status", "priority")


def find_tasks(cursor, filters):
    clauses, params = [], []
    for field in FILTERABLE:
        if field in filters:
            clauses.append(f"{field} = ?")
            params.append(filters[field])
    where = " AND ".join(clauses) or "1=1"
    cursor.execute("SELECT id, title FROM tasks WHERE " + where, params)
    return cursor.fetchall()
