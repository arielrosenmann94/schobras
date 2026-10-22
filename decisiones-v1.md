# Decisiones — Web informativa SCH Obras (v1)

Decisiones tomadas por Ariel. Este documento se irá completando hasta convertirse en el diseño de la v1.

## 2026-10-22

- **Proyectos administrables:** la web tiene un modelo de **Proyectos** y un modelo de **Categorías de proyecto**. Las categorías se crean desde el sistema, no van fijas en el código. Los proyectos los puede cargar la dueña o nosotros.
- **Backoffice propio:** los dueños entran a un backoffice hecho a medida, **no al admin de Django**.
- **Decisiones de diseño y experiencia son nuestras:** WhatsApp, contacto, qué datos se muestran por proyecto, etc. se definen según buenas prácticas de confiabilidad y conversión. No se le consultan a la clienta; a ella solo se le piden datos y contenido.
- **Redes sociales:** fuera de la v1. Entran en la **v1.1**.
- **Correo:** no se le pregunta. Se le informa que debe contratar Google Workspace (o similar) para info@schobras.cl y los correos por persona.
- **Stack:** Django (definido por Ariel).

## 2026-10-22 (tarde) — tras revisar las buenas prácticas de ariel_it

- **Código en inglés, interfaz en español** (como webar, webdfchile, admindf). La app `proyectos` pasa a llamarse `projects`; las rutas públicas siguen en español (`/proyectos/`).
- **PK UUID v7** en todos los modelos, también el usuario (`uuid6`, instructivo/docs/07-appsec/uuid_e_idor.md).
- **django-axes** en el login del panel (5 intentos, 30 min).
- **Entorno agéntico:** las reglas y protecciones al estilo admindf (CLAUDE.md, AGENTS.md, `.claude/settings.json` con deny de secretos Heroku y `git push`) entran en v1; el conector MCP y el resto del entorno agéntico de admindf son parte de v2.0.
- **Servicios como única puerta de escritura** (`projects/services.py`): los usa el panel hoy y la API del conector v2.0 mañana.
- **Seguridad y calidad:** CSP nativa de Django 6, cabeceras, WCAG 2.2 AA, bronce solo en elementos grandes (3,6:1 sobre blanco), backups diarios de Postgres, gates del DoD en cada task, el agente nunca hace push ni deploy.
