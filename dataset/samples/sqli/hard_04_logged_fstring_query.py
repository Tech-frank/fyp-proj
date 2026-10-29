import logging

log = logging.getLogger(__name__)


def fetch_user(cursor, user_id):
    log.debug(f"SELECT * FROM users WHERE id = {user_id}")
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    return cursor.fetchone()
