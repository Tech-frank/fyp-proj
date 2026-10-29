def list_employees(cursor, sort_by):
    cursor.execute(f"SELECT id, name, salary FROM employees ORDER BY {sort_by}")
    return cursor.fetchall()
