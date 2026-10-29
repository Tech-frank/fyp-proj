# Example of a vulnerable query, kept here for documentation only:
#   cursor.execute("SELECT * FROM users WHERE name = '" + name + "'")


def find_by_name(cursor, name):
    cursor.execute("SELECT * FROM users WHERE name = ?", (name,))
    return cursor.fetchall()
