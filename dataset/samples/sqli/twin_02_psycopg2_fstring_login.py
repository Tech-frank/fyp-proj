def check_login(cursor, username, password_hash):
    cursor.execute(
        "SELECT id FROM accounts WHERE username = %s AND pw_hash = %s",
        (username, password_hash),
    )
    return cursor.fetchone() is not None
