# Seguridad y secretos — SCHOBRAS.CL

Estado: active
Owner: Ariel Rosenmann / desarrollador
Última revisión: 2026-10-22
Versión del documento: 1.0.0
Tipo de cambio más reciente: major
Notas del último cambio: línea base de seguridad de la v1.0
Fuente de verdad: sí
Documentos relacionados: ../../../iterap/docs/04-arquitectura/DJANGO_6_BASELINE.md, ../../../instructivo/docs/07-appsec/seguridad_django.md, ../../../iterap/docs/09-devsecops/SECRETS_POLICY.md
Objetivo: definir controles de seguridad, manejo de secretos y modelo de amenazas de la v1.0
Audiencia: seguridad | desarrollo | agentes | ops

---

## Superficie de la v1.0

| Superficie | Riesgo principal | Control |
|---|---|---|
| Páginas públicas | XSS, clickjacking | CSP nativa estricta, autoescape, `X_FRAME_OPTIONS=DENY` |
| Login `/panel/ingresar/` | Fuerza bruta | django-axes (5 intentos → 30 min, por usuario + IP) |
| Panel (subida de fotos) | Archivos maliciosos/pesados | Validación con Pillow (JPEG/PNG/WebP), ≤ 15 MB, storage externo |
| Panel (acciones) | CSRF, IDOR | CSRF en todo POST, cambios de estado solo por POST, UUID v7, permisos por rol |
| Admin de Django | Descubrimiento | `ADMIN_URL` no predecible, solo superusuario |
| Secretos | Exposición en terminal/historial | Reglas de abajo |

## Configuración obligatoria

- **CSP nativa Django 6** (`django.middleware.csp.ContentSecurityPolicyMiddleware`, `SECURE_CSP`):
  `default-src 'self'`; `script-src 'self' 'nonce-…'`; `style-src 'self'`; `img-src 'self' data: https://res.cloudinary.com`; `font-src 'self'`; `connect-src 'self'`; `frame-ancestors 'none'`; `base-uri 'self'`; `form-action 'self'`. Sin `unsafe-inline` ni `unsafe-eval`. Implementación de referencia: `iterap/erp/settings/base.py`.
- `X_FRAME_OPTIONS = "DENY"`, `SECURE_CONTENT_TYPE_NOSNIFF = True`, `SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"`.
- Producción: `SECURE_SSL_REDIRECT`, cookies `Secure`/`HttpOnly`/`SameSite=Lax`, HSTS 1 año con subdominios. **Preload apagado** hasta que el dominio esté estable (warning W021 esperado).
- `SECRET_KEY` ≥ 50 caracteres, solo por variable de entorno.
- `DEBUG = False` en producción; nunca un 500 sin manejar con `DEBUG=True` expuesto.

## Secretos

| Secreto | Dónde vive | Quién lo crea |
|---|---|---|
| `SECRET_KEY` | config var Heroku | Ariel |
| `DATABASE_URL` | add-on Postgres | Heroku |
| `CLOUDINARY_URL` | add-on Cloudinary | Heroku |
| `ADMIN_URL` | config var Heroku | Ariel |

Reglas:
1. Nunca en el repositorio (`.env` está en `.gitignore`; `.env.example` sin valores reales).
2. **Nunca imprimirlos en terminal** (regla dura de admindf, incidente 2026-07-05): prohibido `heroku config`, `heroku config:get VAR` sin `| wc -c`, `heroku releases:info`, `heroku pg:credentials`, `heroku run env`. Bloqueado también en `.claude/settings.json`.
3. Los genera y configura Ariel en su propia terminal; el agente nunca los ve.
4. Rotación: si un secreto aparece en una salida de terminal o en un commit, se rota de inmediato.

## Datos personales

La v1.0 no recolecta datos de visitantes: sin formularios, sin analítica, sin cookies salvo la sesión del panel. Datos personales guardados: solo los usuarios del panel (nombre, correo). Ningún dato de los clientes de la constructora (nunca direcciones).

## Dependencias

Versiones exactas (`==`). `pip-audit -r requirements.txt` sin vulnerabilidades antes de cada despliegue. Una dependencia nueva requiere aprobación de Ariel y mantenimiento activo.

## Backups

`heroku pg:backups:schedule DATABASE_URL --at '04:00 America/Santiago'` (diario). Fotos: Cloudinary.

## Cómo validar que sigue vigente

`manage.py check --deploy` con settings de producción (solo W021), prueba de cabeceras (`core/tests/test_security.py`), prueba de bloqueo de axes, `pip-audit`.

## Cuándo debe actualizarse

Al agregar un formulario público, una API (v2.0), un secreto o una dependencia.
