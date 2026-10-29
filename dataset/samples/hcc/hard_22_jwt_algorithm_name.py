import jwt

token_algorithm = "RS256"


def decode(token_string, public_key):
    return jwt.decode(token_string, public_key, algorithms=[token_algorithm])
