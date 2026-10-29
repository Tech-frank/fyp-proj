from cryptography.fernet import Fernet

ENCRYPTION_KEY = b"ZmDfcTF7_60GrrY167zsiPd67pEvs0aGOv2oasOM1Pg="
cipher = Fernet(ENCRYPTION_KEY)


def protect(text):
    return cipher.encrypt(text.encode())
