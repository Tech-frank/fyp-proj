def page_of_posts(cursor, page, size):
    offset = (int(page) - 1) * int(size)
    cursor.execute("SELECT id, title FROM posts ORDER BY id LIMIT ? OFFSET ?", (int(size), offset))
    return cursor.fetchall()
