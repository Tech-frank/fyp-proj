import os

import mysql.connector


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "orders"),
        password=os.environ["DB_PASSWORD"],
        database="orders",
    )
