class UserRepository:
    def __init__(self, conn):
        self.conn = conn

    def find_by_email(self, email):
        cur = self.conn.cursor()
        cur.execute("SELECT id, name FROM users WHERE email = %s", (email,))
        return cur.fetchone()
