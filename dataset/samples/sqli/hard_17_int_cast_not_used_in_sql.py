def page_number(raw):
    try:
        return max(1, int(raw))
    except ValueError:
        return 1


def fetch_page(cursor, raw_page, size=20):
    page = page_number(raw_page)
    cursor.execute("SELECT id FROM items ORDER BY id LIMIT ? OFFSET ?", (size, (page - 1) * size))
    return cursor.fetchall()
