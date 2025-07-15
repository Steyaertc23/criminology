from .base import *
from dotenv import load_dotenv

load_dotenv(BASE_DIR / "steyaertsite" / "settings" / ".env")

DEBUG = True
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "driven-soviet-poll-copying.trycloudflare.com",
]

CSRF_TRUSTED_ORIGINS = [
    "https://driven-soviet-poll-copying.trycloudflare.com",
]


SECRET_KEY = "django-insecure-jm9*6(8xk_06&p@rhc48!xdm!=7=6=s^)xqia2canf-j4$uztp"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": BASE_DIR / "temp" / "django_cache",
    }
}
# CORS_ALLOW_ALL_ORIGINS = True
