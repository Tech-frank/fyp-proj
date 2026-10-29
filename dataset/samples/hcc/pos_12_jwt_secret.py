import datetime

import jwt

JWT_SECRET = "9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d"
JWT_ALGORITHM = "HS256"


def issue_token(user_id):
    payload = {
        "sub": str(user_id),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
