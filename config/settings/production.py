"""
config/settings/production.py
─────────────────────────────
Settings de producción para Heroku.
Las fotos van a Cloudinary (CLOUDINARY_URL, lo define el add-on de Heroku).
"""
import dj_database_url
from decouple import config
from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F401, F403


def csv_config(name, default):
    return [value.strip() for value in config(name, default=default).split(",") if value.strip()]


DEBUG = False

# www.schobras.cl -> schobras.cl (justo después de SecurityMiddleware)
MIDDLEWARE.insert(1, "core.middleware.CanonicalHostMiddleware")  # noqa: F405
ALLOWED_HOSTS = csv_config("ALLOWED_HOSTS", "schobras.cl,www.schobras.cl")
CSRF_TRUSTED_ORIGINS = csv_config("CSRF_TRUSTED_ORIGINS", "https://schobras.cl,https://www.schobras.cl")

DATABASES = {
    "default": dj_database_url.config(conn_max_age=600, ssl_require=True),
}

# ── Fotos en Cloudinary ───────────────────────────────────────────────────────
# El disco de Heroku es efímero: sin Cloudinary las fotos se perderían.
if not config("CLOUDINARY_URL", default=""):
    raise ImproperlyConfigured("Falta CLOUDINARY_URL")
INSTALLED_APPS += ["cloudinary_storage", "cloudinary"]  # noqa: F405
STORAGES["default"] = {"BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage"}  # noqa: F405

# ── SSL / HTTPS (Heroku) ──────────────────────────────────────────────────────
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Tras el router de Heroku REMOTE_ADDR es la IP del router; axes debe usar la
# IP real o cinco intentos fallidos de cualquiera bloquearían a todos.
# AXES_CLIENT_IP_CALLABLE (axes/helpers.py get_client_ip_address) se usa en vez
# de AXES_IPWARE_*, que exige django-ipware (no instalado ni aprobado).
AXES_CLIENT_IP_CALLABLE = "panel.client_ip.get_client_ip"

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
