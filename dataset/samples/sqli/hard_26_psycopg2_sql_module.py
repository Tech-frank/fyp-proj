from psycopg2 import sql


def count_in(cursor, table):
    query = sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(table))
    cursor.execute(query)
    return cursor.fetchone()[0]
