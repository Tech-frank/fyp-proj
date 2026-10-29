def check_login(cursor, username, password_hash):
    cursor.execute(
        f"SELECT id FROM accounts WHERE username = '{username}' AND pw_hash = '{password_hash}'"
    )
    return cursor.fetchone() is not None
