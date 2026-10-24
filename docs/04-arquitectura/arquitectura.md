# Arquitectura — SCHOBRAS.CL

Estado: active
Owner: Ariel Rosenmann / desarrollador
Última revisión: 2026-10-22
Versión del documento: 1.0.0
Tipo de cambio más reciente: major
Notas del último cambio: arquitectura inicial de la v1.0
Fuente de verdad: sí
Documentos relacionados: adr/, ../03-dominio/modelo-de-datos.md, ../2026-10-22-v2-decision-arquitectura.md
Objetivo: describir cómo está construida la v1.0 y por qué
Audiencia: arquitectura | desarrollo | agentes

---

## Stack

Python 3.12 · Django 6.0.6 · PostgreSQL (Heroku `essential-0`) / SQLite (local) · WhiteNoise · gunicorn · Amazon S3 `sa-east-1` con `django-storages` + `boto3` (fotos, ADR-0006; pendiente) · `uuid6` · `django-axes`. Sin frameworks de frontend; CSS y JS propios. Alineado con iterap e iterap_com.

## Estructura

```
config/            settings (base, local, production), urls, wsgi
accounts/          User (UUID v7, rol editora/administrador)
core/              BaseModel, SiteSettings, inicio, SEO (sitemap, robots, JSON-LD), 404, template tags
projects/          Category, Project, ProjectPhoto, services.py (única puerta de escritura), páginas públicas
panel/             backoffice /panel/ (CBV), permisos, formularios
templates/         base.html, includes/, 404.html
static/            css/site.css, css/panel.css, js/site.js, fonts/, img/
docs/              documentación (índice en docs/README.md)
```

## Rutas

| Ruta | Nombre | Acceso |
|---|---|---|
| `/` | `core:home` | público |
| `/proyectos/` | `projects:list` | público |
| `/proyectos/categoria/<slug>/` | `projects:category` | público |
| `/proyectos/<slug>/` | `projects:detail` | público |
| `/sitemap.xml`, `/robots.txt` | | público |
| `/panel/…` | `panel:*` | usuarios autenticados (rol según vista) |
| `/<ADMIN_URL>` | admin de Django | solo Ariel, emergencias |

## Flujo de datos

```
Visitante ──GET──▶ vistas públicas ──▶ Project.objects.published() ──▶ plantillas (variantes WebP 400/800/1600 en S3)
Claudia ──POST──▶ panel (CBV + forms) ──▶ projects/services.py ──▶ modelos
Ariel ──▶ admin de Django ──▶ acciones que llaman a services.py
(v2.0) Claude Desktop ──MCP──▶ API Django ──▶ projects/services.py
```

## Decisiones

| ADR | Tema |
|---|---|
| [ADR-0001](adr/ADR-0001-uuid-v7.md) | PK UUID v7 |
| [ADR-0002](adr/ADR-0002-cloudinary.md) | ~~Fotos en Cloudinary~~ (reemplazado por ADR-0006) |
| [ADR-0003](adr/ADR-0003-idioma-codigo.md) | Código en inglés, interfaz en español |
| [ADR-0004](adr/ADR-0004-servicios-unica-puerta.md) | `services.py` como única puerta de escritura |
| [ADR-0005](adr/ADR-0005-panel-propio.md) | Backoffice propio en vez del admin de Django |
| [ADR-0006](adr/ADR-0006-fotos-s3.md) | Fotos en Amazon S3 `sa-east-1` con variantes WebP de Pillow |

## Entornos

| Entorno | Settings | Base de datos | Fotos |
|---|---|---|---|
| Local | `config.settings.local` | SQLite | `media/` |
| Producción | `config.settings.production` | Postgres (`DATABASE_URL`) | S3 (ADR-0006). Hasta implementarlo: sin almacenamiento y `PHOTO_UPLOADS_ENABLED=False` |

## Cuándo debe actualizarse

Al agregar una app, una ruta de primer nivel, una dependencia o un entorno.
