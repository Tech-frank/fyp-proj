def autocomplete(cursor, prefix):
    pattern = prefix + "%"
    cursor.execute("SELECT name FROM cities WHERE name LIKE '" + pattern + "' LIMIT 10")
    return [r[0] for r in cursor.fetchall()]
