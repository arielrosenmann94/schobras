"""
config/settings/production.py
─────────────────────────────
Settings de producción para Heroku.
El almacenamiento de fotos (Cloudinary o S3) se agrega cuando se defina quién
es dueño de esas cuentas (pendiente en docs/2026-10-22-web-v1-diseno.md).
"""
import dj_database_url
from decouple import config

from .base import *  # noqa: F401, F403


def csv_config(name, default):
    return [value.strip() for value in config(name, default=default).split(",") if value.strip()]


DEBUG = False
ALLOWED_HOSTS = csv_config("ALLOWED_HOSTS", "schobras.cl,www.schobras.cl")
CSRF_TRUSTED_ORIGINS = csv_config("CSRF_TRUSTED_ORIGINS", "https://schobras.cl,https://www.schobras.cl")

DATABASES = {
    "default": dj_database_url.config(conn_max_age=600, ssl_require=True),
}

# ── SSL / HTTPS (Heroku) ──────────────────────────────────────────────────────
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# ── Cookies seguras ────────────────────────────────────────────────────────────
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

# ── HSTS ─────────────────────────────────────────────────────────────────────
SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", default=31536000, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = config("SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True, cast=bool)
SECURE_HSTS_PRELOAD = config("SECURE_HSTS_PRELOAD", default=False, cast=bool)

# ── Logs a la consola de Heroku ────────────────────────────────────────────────
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}
