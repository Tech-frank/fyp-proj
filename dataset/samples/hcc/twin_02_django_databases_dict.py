# settings.py (excerpt)
import os

DEBUG = False
ALLOWED_HOSTS = ["shop.example.com"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "shop",
        "USER": "shop_app",
        "PASSWORD": os.environ.get("SHOP_DB_PASSWORD"),
        "HOST": "db.internal",
        "PORT": "5432",
    }
}
