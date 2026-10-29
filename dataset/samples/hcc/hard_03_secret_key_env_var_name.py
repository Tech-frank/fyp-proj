import os

SECRET_KEY_ENV_VAR = "DJANGO_SECRET_KEY"


def load_secret_key():
    value = os.environ.get(SECRET_KEY_ENV_VAR)
    if not value:
        raise RuntimeError(f"{SECRET_KEY_ENV_VAR} is not set")
    return value
