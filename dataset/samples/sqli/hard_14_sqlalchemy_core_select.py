from sqlalchemy import select

from .tables import accounts


def account_by_number(conn, number):
    stmt = select(accounts).where(accounts.c.number == number)
    return conn.execute(stmt).first()
