ALLOWED_SORT = {"name": "name", "salary": "salary", "id": "id"}


def list_employees(cursor, sort_by):
    column = ALLOWED_SORT.get(sort_by, "id")
    cursor.execute(f"SELECT id, name, salary FROM employees ORDER BY {column}")
    return cursor.fetchall()
