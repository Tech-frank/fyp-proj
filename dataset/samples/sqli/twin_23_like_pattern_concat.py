def autocomplete(cursor, prefix):
    pattern = prefix + "%"
    cursor.execute("SELECT name FROM cities WHERE name LIKE ? LIMIT 10", (pattern,))
    return [r[0] for r in cursor.fetchall()]
