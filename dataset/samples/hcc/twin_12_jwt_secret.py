import datetime
import os

import jwt

JWT_SECRET = os.environ["JWT_SECRET"]
JWT_ALGORITHM = "HS256"


def issue_token(user_id):
    payload = {
        "sub": str(user_id),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
