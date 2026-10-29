TABLE = "user_accounts"


def count_accounts(cursor):
    cursor.execute("SELECT COUNT(*) FROM " + TABLE)
    return cursor.fetchone()[0]
