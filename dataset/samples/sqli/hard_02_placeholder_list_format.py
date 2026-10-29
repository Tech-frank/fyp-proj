def products_by_ids(cursor, ids):
    query = "SELECT sku, name FROM products WHERE id IN ({})".format(",".join("?" * len(ids)))
    cursor.execute(query, ids)
    return cursor.fetchall()
