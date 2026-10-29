TABLE_PREFIX = "app_"


def table(name):
    return TABLE_PREFIX + name


def drop_temp_tables(cursor):
    for name in ("tmp_import", "tmp_export"):
        cursor.execute("DROP TABLE IF EXISTS " + table(name))
