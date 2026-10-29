SEARCHABLE = {"email", "phone"}


def build_lookup(field):
    if field not in SEARCHABLE:
        raise ValueError(field)
    return "SELECT * FROM customers WHERE " + field + " = ?"


def lookup_customer(cursor, field, value):
    cursor.execute(build_lookup(field), (value,))
    return cursor.fetchone()
