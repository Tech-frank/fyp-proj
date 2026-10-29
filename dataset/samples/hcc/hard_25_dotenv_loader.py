import os

from dotenv import load_dotenv

load_dotenv()
DB_PASSWORD = os.getenv("DB_PASSWORD")
dotenv_password_key = "DB_PASSWORD"


def has_db_password():
    return bool(os.getenv(dotenv_password_key))
