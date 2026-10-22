# SCHOBRAS.CL

Web de Constructora Schonffeldt SpA: web informativa (v1.0) con catálogo de proyectos administrable y backoffice propio.

- Diseño v1.0: [docs/2026-10-22-web-v1-diseno.md](docs/2026-10-22-web-v1-diseno.md)
- Decisiones: [decisiones-v1.md](decisiones-v1.md)
- Respuestas de la clienta: [respuestas-cliente-2026-10-22.md](respuestas-cliente-2026-10-22.md)

## Stack

Python 3.12 · Django 6.0 · PostgreSQL (producción) / SQLite (local) · WhiteNoise · gunicorn · Heroku.

## Apps

| App | Qué contiene |
|---|---|
| `accounts` | Usuario propio (`accounts.User`) y roles |
| `core` | Páginas públicas: inicio, 404, sitemap, robots |
| `projects` | Proyectos, categorías y fotos |
| `panel` | Backoffice para los dueños (no el admin de Django) |

## Desarrollo local

```bash
python3.12 -m venv env_schobras
source env_schobras/bin/activate
pip install -r requirements.txt
cp .env.example .env   # y poner un SECRET_KEY
python manage.py migrate
python manage.py runserver
```

Settings: `config.settings.local` (por defecto en `manage.py`) y `config.settings.production` (por defecto en `wsgi.py`).

## Producción (Heroku)

Variables: `SECRET_KEY`, `DJANGO_SETTINGS_MODULE=config.settings.production`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `ADMIN_URL` y `DATABASE_URL` (add-on de Postgres). El `Procfile` migra en cada release.
