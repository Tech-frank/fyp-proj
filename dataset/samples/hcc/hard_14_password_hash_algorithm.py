from passlib.context import CryptContext

PASSWORD_HASH_SCHEME = "argon2"
pwd_context = CryptContext(schemes=[PASSWORD_HASH_SCHEME], deprecated="auto")


def hash_password(plain):
    return pwd_context.hash(plain)


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)
