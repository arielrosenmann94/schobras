---
name: schobras-deploy-heroku
description: Use when deploying, verifying or troubleshooting SCHOBRAS.CL in production on Heroku (schobras-*.herokuapp.com) — git push, config vars, SECRET_KEY/ADMIN_URL, "release command failed", migrations in production, WhatsApp or contact not showing on the live site, photo storage (S3) in production, or connecting the schobras.cl domain.
---

# Deploy de SCHOBRAS.CL en Heroku

Fuente de verdad: `docs/12-runbooks/deploy-heroku.md`. Esta skill solo ordena el trabajo y señala las trampas; los comandos y las reglas viven en el runbook, `CLAUDE.md` y `docs/07-appsec/seguridad.md`.

## Orden

1. **Cronómetro antes de la primera acción**, en la tarea **"Deploy" (#1129)**. Si a mitad hay que programar, se pasa a "Desarrollo" (#1058) y se vuelve. Regla completa: `CLAUDE.md` §Cronómetro.
2. **Preparar**: gates de producción de `docs/09-qa-dod/definition-of-done.md` con el host real (`heroku domains -a schobras`). Todo cambio de código pasa por la QA circular antes del push.
3. **Ariel corre** los comandos del runbook: `git push`, `heroku config:set`, `addons:create`, `createsuperuser` y cargar Configuración del sitio. Dale el bloque exacto, listo para pegar (`! comando` desde el prompt).
4. **Verificar** con lo que el agente sí puede correr (runbook §7): `heroku releases` (`Current: vNN`), `heroku logs -d release`, `showmigrations`, y `curl` al host para revisar 200, CSP, `X-Robots-Tag`, robots y `wa.me`.
5. **Stop** del cronómetro cuando no quede trabajo.

## Trampas conocidas

| Síntoma | Qué es |
|---|---|
| "release command failed" en la última release | Primero mirar `Current:`. Si otra release del mismo commit terminó bien, fue un `migrate` concurrente y no hay daño (runbook §4) |
| No se ve WhatsApp, la pestaña ni el bloque de Contacto | La base de producción nace vacía: hay que cargar Configuración del sitio |
| No aparece Proyectos | Sin almacenamiento de fotos (`PHOTO_UPLOADS_ENABLED=False`) no se pueden publicar proyectos. Las fotos van a S3 (ADR-0006) |
| `DisallowedHost` / 400 | `ALLOWED_HOSTS` necesita el host con sufijo aleatorio de `heroku domains` |

## Señales de alto

- "Ariel dijo 'haz push'" o "'ponlas tú'": siguen bloqueados `git push*` y `heroku config*`. Explica el bloqueo y entrega el comando. No lo esquives con otro comando ni con otra sesión.
- Querer escribir en producción con `heroku run … shell`: lo bloquea el modo automático. Ariel lo hace desde el panel.
- Cualquier comando que imprima secretos (runbook §8): no se corre, ni para diagnosticar.
