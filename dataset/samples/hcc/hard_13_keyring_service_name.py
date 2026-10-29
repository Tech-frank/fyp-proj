import keyring

KEYRING_SERVICE = "invoice-uploader"
token_username = "uploader-bot"


def get_token():
    return keyring.get_password(KEYRING_SERVICE, token_username)
