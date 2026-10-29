class AuditLog:
    TABLE = "audit_events"

    def __init__(self, cursor):
        self.cursor = cursor

    def events_for(self, actor):
        statement = f"SELECT action, at FROM {self.TABLE} WHERE actor = ?"
        self.cursor.execute(statement, (actor,))
        return self.cursor.fetchall()
