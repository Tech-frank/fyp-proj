import os


class ProductionConfig:
    DEBUG = False
    SIGNING_ALGORITHM = "RS256"
    with open(os.environ["SIGNING_KEY_PATH"], encoding="utf-8") as _fh:
        PRIVATE_KEY = _fh.read()
