def users_by_ids(cursor, ids_csv):
    ids = [part.strip() for part in ids_csv.split(",") if part.strip()]
    placeholders = ",".join("?" * len(ids))
    cursor.execute("SELECT id, name FROM users WHERE id IN (" + placeholders + ")", ids)
    return cursor.fetchall()
