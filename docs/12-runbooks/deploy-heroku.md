# Runbook — Despliegue en Heroku — SCHOBRAS.CL

Estado: active
Owner: Ariel Rosenmann / desarrollador
Última revisión: 2026-10-23
Versión del documento: 1.1.0
Tipo de cambio más reciente: minor
Notas del último cambio: primer despliegue sin dominio propio (*.herokuapp.com, sin indexar); schobras.cl se conecta después
Fuente de verdad: sí
Documentos relacionados: ../07-appsec/seguridad.md, ../../../iterap_com/docs/12-runbooks/deploy_heroku.md, ../../../iterap/docs/11-runbooks/HEROKU_PRODUCTION_DEPLOY.md
Objetivo: pasos exactos para crear, desplegar, verificar y revertir la app en Heroku
Audiencia: ops | desarrollo

---

> **Solo Ariel ejecuta este runbook.** El agente no corre `heroku create`, no hace push y no despliega.
> Cuentas: Heroku y (cuando se implemente) Amazon S3 a nombre de Claudia Schonffeldt, pagadas con la tarjeta de la empresa; Ariel con acceso de colaborador.

## 0. Antes de empezar

- Gates de producción de `docs/09-qa-dod/definition-of-done.md` en verde.
- `main` al día y subido a GitHub (`git push origin main`).

**Primero va sin dominio propio** (decisión de Ariel, 2026-10-23): la web queda en el host que asigna Heroku (`schobras-<sufijo>.herokuapp.com`) y **no se indexa** en buscadores (`SEARCH_INDEXING` apagado: `robots.txt` con `Disallow: /` y cabecera `X-Robots-Tag: noindex, nofollow`). schobras.cl se conecta en la §5.

## 1. Crear la app (una vez)

```bash
heroku create schobras --region us
heroku buildpacks:set heroku/python -a schobras
heroku addons:create heroku-postgresql:essential-0 -a schobras
heroku pg:backups:schedule DATABASE_URL --at '04:00 America/Santiago' -a schobras
# Fotos: en este primer deploy de muestra NO hay almacenamiento externo (S3 viene
# después). Sin él la web arranca, pero el panel y el admin no aceptan fotos
# ("La subida de fotos se habilita muy pronto."), porque el disco de Heroku se borra.
```

## 2. Config vars (en tu terminal; nunca las imprimas después)

Las apps nuevas de Heroku tienen un host con sufijo aleatorio (`schobras-<sufijo>.herokuapp.com`). Se lee de `heroku domains` (no muestra secretos) y se usa en `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS`:

```bash
HEROKU_HOST="$(heroku domains -a schobras --json | python3 -c 'import json,sys; print(next(d["hostname"] for d in json.load(sys.stdin) if d["kind"] == "heroku"))')"
echo "$HEROKU_HOST"     # debe verse como schobras-xxxxxxxxxxxx.herokuapp.com

ADMIN_PATH="$(python3 -c 'import secrets; print(secrets.token_urlsafe(12))')/"
echo "Ruta del admin: https://$HEROKU_HOST/$ADMIN_PATH"   # guárdala en tu gestor de contraseñas

heroku config:set -a schobras \
  DJANGO_SETTINGS_MODULE=config.settings.production \
  SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_urlsafe(64))')" \
  ADMIN_URL="$ADMIN_PATH" \
  ALLOWED_HOSTS="$HEROKU_HOST" \
  CSRF_TRUSTED_ORIGINS="https://$HEROKU_HOST"
```

`SEARCH_INDEXING` no se define: en producción viene apagado. Para comprobar que una variable existe: `heroku config:get VAR -a schobras | wc -c` (nunca sin `| wc -c`).

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

- Abrir `https://$HEROKU_HOST/` (inicio, `/proyectos/`, `/sitemap.xml`, una URL inexistente → 404 con marca). `/robots.txt` debe decir `Disallow: /` y `curl -sI https://$HEROKU_HOST/ | grep -i x-robots-tag` debe mostrar `noindex, nofollow`.
- En el admin: cargar **Configuración del sitio** con al menos un canal (WhatsApp/teléfono/correo).
- En el admin: crear a Claudia (oficina@claudiaarquitecta.cl, rol Editora) y probar `/panel/ingresar/`.
- Lighthouse móvil (Chrome DevTools): rendimiento y accesibilidad ≥ 90.

## 5. Dominio (cuando Claudia entregue el acceso al registrador)

```bash
heroku domains:add schobras.cl -a schobras
heroku domains:add www.schobras.cl -a schobras
heroku certs:auto:enable -a schobras
# Se vuelve a leer el host: esta sección puede correrse otro día, en otra terminal.
HEROKU_HOST="$(heroku domains -a schobras --json | python3 -c 'import json,sys; print(next(d["hostname"] for d in json.load(sys.stdin) if d["kind"] == "heroku"))')"
test -n "$HEROKU_HOST" && heroku config:set -a schobras \
  ALLOWED_HOSTS="$HEROKU_HOST,schobras.cl,www.schobras.cl" \
  CSRF_TRUSTED_ORIGINS="https://$HEROKU_HOST,https://schobras.cl,https://www.schobras.cl" \
  SEARCH_INDEXING=True
```

Si `HEROKU_HOST` viene vacío, el `config:set` no se ejecuta (sin cerrar la terminal): revisar `heroku domains -a schobras`. Con `SEARCH_INDEXING=True` vuelven `robots.txt` normal (con `Sitemap:`) y la indexación; comprobar que `curl -sI https://schobras.cl/` ya no trae `X-Robots-Tag`.

En el registrador (Registrar.eu o su revendedor): registros que indique `heroku domains` (ALIAS/ANAME o CNAME). `www` redirige (301) a `schobras.cl` con `core.middleware.CanonicalHostMiddleware`, activo solo en producción; basta con apuntar ambos nombres a Heroku.

## 6. Rollback

```bash
heroku releases -a schobras
heroku rollback vNN -a schobras
```

Si la release fallida migró la base, revisar la migración antes de volver a desplegar; restaurar backup solo si hubo pérdida de datos: `heroku pg:backups:restore <backup> DATABASE_URL -a schobras`.

## 7. Prohibido

`heroku config` (sin `:get … | wc -c`), `heroku releases:info`, `heroku pg:credentials`, `heroku run env`. Ver `docs/07-appsec/seguridad.md`.
