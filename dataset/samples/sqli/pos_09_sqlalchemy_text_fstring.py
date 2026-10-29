from sqlalchemy import text


def recent_logins(engine, username):
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT at FROM logins WHERE username = '{username}' ORDER BY at DESC"))
        return [row.at for row in result]
