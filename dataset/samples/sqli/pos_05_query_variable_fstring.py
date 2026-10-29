def search_products(cursor, term):
    query = f"SELECT sku, name, price FROM products WHERE name LIKE '%{term}%'"
    cursor.execute(query)
    return cursor.fetchall()
