import os

from cryptography.fernet import Fernet

ENCRYPTION_KEY = os.environ["APP_ENCRYPTION_KEY"].encode()
cipher = Fernet(ENCRYPTION_KEY)


def protect(text):
    return cipher.encrypt(text.encode())
