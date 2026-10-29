def search_products(cursor, term):
    query = "SELECT sku, name, price FROM products WHERE name LIKE ?"
    cursor.execute(query, (f"%{term}%",))
    return cursor.fetchall()
