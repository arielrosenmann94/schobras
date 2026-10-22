"""
config/settings/local.py
────────────────────────
Settings para desarrollo local. NUNCA usar en producción.
"""
import sys

from .base import *  # noqa: F401, F403

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

if "test" in sys.argv:
    DATABASES["default"]["NAME"] = ":memory:"

# En local no se fuerza SSL ni se usa el manifiesto de estáticos.
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
STORAGES["staticfiles"] = {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}

# Email local: se imprime en consola.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
