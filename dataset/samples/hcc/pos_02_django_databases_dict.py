# settings.py (excerpt)
DEBUG = False
ALLOWED_HOSTS = ["shop.example.com"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "shop",
        "USER": "shop_app",
        "PASSWORD": "Wq7!pZr2#Lm9vT",
        "HOST": "db.internal",
        "PORT": "5432",
    }
}
