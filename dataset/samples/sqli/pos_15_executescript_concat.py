import sqlite3


def reset_user_data(db_path, username):
    conn = sqlite3.connect(db_path)
    conn.executescript(
        "DELETE FROM sessions WHERE user = '" + username + "';"
        "DELETE FROM carts WHERE user = '" + username + "';"
    )
    conn.close()
