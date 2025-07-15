from .base import *
from criminology.settings import get_secret

SECRET_KEY = get_secret("SECRET_KEY")

DEBUG = False
raw_hosts = get_secret("ALLOWED_HOSTS", "")
ALLOWED_HOSTS = [host.strip() for host in raw_hosts.split(",") if host.strip()]

raw_origins = get_secret("CSRF_TRUSTED_ORIGINS", "")
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"{get_secret('REDIS_CACHE', 'redis://127.0.0.1:6379/1')}",  # Adjust if using Docker or different port/db
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
DATABASES = {
    "default": {
        'ENGINE': f"django.db.backends.{get_secret("DATABASE_ENGINE", "sqlite3")}",
        'NAME': get_secret("DATABASE_NAME", "criminology"),
        'USER':get_secret("DATABASE_USERNAME", 'admin'),
        'PASSWORD':get_secret('DATABASE_PASSWORD', "admin"),
        'HOST':get_secret('DATABASE_HOST', 'db'),
        'PORT':get_secret("DATABASE_PORT", 5432)
    }
}

CELERY_BROKER_URL = f"{get_secret('REDIS_BROKER', 'redis://localhost:6379/0')}"

SECURE_SSL_REDIRECT = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
