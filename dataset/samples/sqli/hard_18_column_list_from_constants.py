EXPORT_COLUMNS = ("id", "email", "created_at")


def export_users(cursor):
    columns = ", ".join(EXPORT_COLUMNS)
    cursor.execute("SELECT " + columns + " FROM users")
    return cursor.fetchall()
