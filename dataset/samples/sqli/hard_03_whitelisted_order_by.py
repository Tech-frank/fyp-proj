SORTABLE = {"newest": "created_at DESC", "oldest": "created_at ASC", "title": "title ASC"}


def list_articles(cursor, sort="newest"):
    order = SORTABLE.get(sort, SORTABLE["newest"])
    cursor.execute(f"SELECT id, title FROM articles ORDER BY {order}")
    return cursor.fetchall()
