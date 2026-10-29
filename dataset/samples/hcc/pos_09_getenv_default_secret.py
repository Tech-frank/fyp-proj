import os

import mysql.connector


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "orders"),
        password=os.getenv("DB_PASSWORD", "0rders#Prod2024"),
        database="orders",
    )
