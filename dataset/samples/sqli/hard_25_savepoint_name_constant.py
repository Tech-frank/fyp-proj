SAVEPOINT = "before_import"


def import_batch(cursor, rows):
    cursor.execute(f"SAVEPOINT {SAVEPOINT}")
    try:
        cursor.executemany("INSERT INTO staging (a, b) VALUES (?, ?)", rows)
    except Exception:
        cursor.execute(f"ROLLBACK TO SAVEPOINT {SAVEPOINT}")
        raise
