def bulk_tag(cursor, tag, ids):
    cursor.executemany("INSERT INTO item_tags (item_id, tag) VALUES (?, ?)",
                       [(i, tag) for i in ids])
