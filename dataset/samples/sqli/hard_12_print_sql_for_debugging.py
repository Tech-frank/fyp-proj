def run(cursor, statement, params=()):
    print("Executing: " + statement)
    cursor.execute(statement, params)
    return cursor.fetchall()
