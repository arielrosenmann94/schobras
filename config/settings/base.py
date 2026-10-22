"""
config/settings/base.py
───────────────────────
Configuración base compartida entre todos los ambientes de SCHOBRAS.CL.
No contiene secretos: los valores sensibles llegan por variables de entorno
con python-decouple (ver .env.example).
Diseño: docs/2026-10-22-web-v1-diseno.md.
"""
from pathlib import Path

from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ── Seguridad ──────────────────────────────────────────────────────────────────
SECRET_KEY = config("SECRET_KEY")

# Usuario propio desde el día uno: cambiarlo después de la primera migración
# es muy costoso. Los roles (editora / administrador) se definen en el plan.
AUTH_USER_MODEL = "accounts.User"

# Ruta del admin de Django (solo emergencias, lo usa Ariel). Configurable para
# no dejarla en /admin/ en producción.
ADMIN_URL = config("ADMIN_URL", default="admin/")

# ── Aplicaciones ───────────────────────────────────────────────────────────────
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
]

LOCAL_APPS = [
    "accounts",   # usuarios y roles
    "core",       # páginas públicas: inicio, 404, sitemap, robots
    "projects",   # proyectos, categorías y fotos
    "panel",      # backoffice propio (no el admin de Django)
]

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ── Base de datos ──────────────────────────────────────────────────────────────
# Se define en local.py (SQLite) y production.py (PostgreSQL vía DATABASE_URL).

# ── Contraseñas ────────────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ── Internacionalización ───────────────────────────────────────────────────────
LANGUAGE_CODE = "es-cl"
TIME_ZONE = "America/Santiago"
USE_I18N = True
USE_TZ = True

# ── Archivos estáticos y subidos ───────────────────────────────────────────────
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── Sesión del panel ───────────────────────────────────────────────────────────
LOGIN_URL = "/panel/ingresar/"
LOGIN_REDIRECT_URL = "/panel/"
LOGOUT_REDIRECT_URL = "/"
