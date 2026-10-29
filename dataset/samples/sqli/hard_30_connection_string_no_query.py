import sqlite3


def open_db(name):
    path = f"data/{name}.sqlite3"
    return sqlite3.connect(path)
