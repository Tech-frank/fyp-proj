class QueryError(Exception):
    pass


def require_rows(rows, table):
    if not rows:
        raise QueryError(f"No rows returned from {table}; check the WHERE clause.")
    return rows
