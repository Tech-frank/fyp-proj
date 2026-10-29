def build_lookup(field, value):
    return "SELECT * FROM customers WHERE " + field + " = '" + value + "'"


def lookup_customer(cursor, field, value):
    cursor.execute(build_lookup(field, value))
    return cursor.fetchone()
