def users_by_ids(cursor, ids_csv):
    cursor.execute("SELECT id, name FROM users WHERE id IN (" + ids_csv + ")")
    return cursor.fetchall()
