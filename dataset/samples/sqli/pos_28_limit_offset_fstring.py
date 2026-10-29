def page_of_posts(cursor, page, size):
    offset = (int(page) - 1) * int(size)
    cursor.execute(f"SELECT id, title FROM posts ORDER BY id LIMIT {size} OFFSET {offset}")
    return cursor.fetchall()
