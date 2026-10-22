# Runbook — Despliegue en Heroku — SCHOBRAS.CL

Estado: active
Owner: Ariel Rosenmann / desarrollador
Última revisión: 2026-10-22
Versión del documento: 1.0.0
Tipo de cambio más reciente: major
Notas del último cambio: runbook inicial de la v1.0
Fuente de verdad: sí
Documentos relacionados: ../07-appsec/seguridad.md, ../../../iterap_com/docs/12-runbooks/deploy_heroku.md, ../../../iterap/docs/11-runbooks/HEROKU_PRODUCTION_DEPLOY.md
Objetivo: pasos exactos para crear, desplegar, verificar y revertir la app en Heroku
Audiencia: ops | desarrollo

---

> **Solo Ariel ejecuta este runbook.** El agente no corre `heroku create`, no hace push y no despliega.
> Cuentas: Heroku y Cloudinary a nombre de Claudia Schonffeldt, pagadas con la tarjeta de la empresa; Ariel con acceso de colaborador.

## 0. Antes de empezar

- Gates de producción de `docs/09-qa-dod/definition-of-done.md` en verde.
- `git status` limpio en `main`.

## 1. Crear la app (una vez)

```bash
heroku create schobras --region us
heroku buildpacks:set heroku/python -a schobras
heroku addons:create heroku-postgresql:essential-0 -a schobras
heroku pg:backups:schedule DATABASE_URL --at '04:00 America/Santiago' -a schobras
heroku addons:create cloudinary:starter -a schobras     # define CLOUDINARY_URL
```

## 2. Config vars (en tu terminal; nunca las imprimas después)

```bash
heroku config:set -a schobras \
  DJANGO_SETTINGS_MODULE=config.settings.production \
  SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_urlsafe(64))')" \
  ADMIN_URL="$(python3 -c 'import secrets; print(secrets.token_urlsafe(12))')/" \
  ALLOWED_HOSTS="schobras.herokuapp.com,schobras.cl,www.schobras.cl" \
  CSRF_TRUSTED_ORIGINS="https://schobras.herokuapp.com,https://schobras.cl,https://www.schobras.cl"
```

Guarda el `ADMIN_URL` en tu gestor de contraseñas. Para comprobar que una variable existe: `heroku config:get VAR -a schobras | wc -c` (nunca sin `| wc -c`).

## 3. Desplegar

```bash
git remote add heroku https://git.heroku.com/schobras.git   # una vez
git push heroku main
```

El `Procfile` corre `migrate` en `release`; Heroku corre `collectstatic` en el build.

## 4. Verificar

```bash
heroku releases -a schobras                 # la última release debe estar "succeeded"
heroku run python manage.py showmigrations -a schobras   # sin [ ] pendientes
heroku run python manage.py createsuperuser -a schobras  # solo la primera vez
heroku logs --tail -a schobras              # sin errores al navegar
```

- Abrir `https://schobras.herokuapp.com/` (inicio, `/proyectos/`, `/robots.txt`, `/sitemap.xml`, una URL inexistente → 404 con marca).
- En el admin: cargar **Configuración del sitio** con al menos un canal (WhatsApp/teléfono/correo).
- En el admin: crear a Claudia (oficina@claudiaarquitecta.cl, rol Editora) y probar `/panel/ingresar/`.
- Lighthouse móvil (Chrome DevTools): rendimiento y accesibilidad ≥ 90.

## 5. Dominio (cuando Claudia entregue el acceso al registrador)

```bash
heroku domains:add schobras.cl -a schobras
heroku domains:add www.schobras.cl -a schobras
heroku certs:auto:enable -a schobras
```

En el registrador (Registrar.eu o su revendedor): registros que indique `heroku domains` (ALIAS/ANAME o CNAME). `www` redirige a `schobras.cl`.

## 6. Rollback

```bash
heroku releases -a schobras
heroku rollback vNN -a schobras
```

Si la release fallida migró la base, revisar la migración antes de volver a desplegar; restaurar backup solo si hubo pérdida de datos: `heroku pg:backups:restore <backup> DATABASE_URL -a schobras`.

## 7. Prohibido

`heroku config` (sin `:get … | wc -c`), `heroku releases:info`, `heroku pg:credentials`, `heroku run env`. Ver `docs/07-appsec/seguridad.md`.
