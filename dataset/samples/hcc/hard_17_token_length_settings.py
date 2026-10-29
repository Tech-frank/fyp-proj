import secrets

TOKEN_BYTES = 32
token_alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"


def new_reset_token():
    return "".join(secrets.choice(token_alphabet) for _ in range(TOKEN_BYTES))
