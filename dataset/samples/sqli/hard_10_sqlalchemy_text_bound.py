from sqlalchemy import text

ACTIVE_FILTER = "status = 'active'"


def active_members(conn, club_id):
    stmt = text("SELECT name FROM members WHERE club_id = :club AND " + ACTIVE_FILTER)
    return conn.execute(stmt, {"club": club_id}).fetchall()
