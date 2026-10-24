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

## 2026-10-22 — v1.1

- **Panel instalable (PWA) con inicio por huella digital** (WebAuthn/passkeys), igual que iterap y admindf: huella como acción principal del login, contraseña como respaldo. Se implementa copiando y adaptando `iterap/accounts/webauthn_utils.py`, sus vistas, JS, manifest y service worker. Se activa cuando `schobras.cl` esté conectado (las passkeys quedan atadas al dominio). Detalle: `docs/2026-10-22-web-v1.1-diseno.md` §2.6.

## 2026-10-23 — respuestas finales de la clienta (respuestas-cliente-2026-10-23.md)

- **Oferta de arquitectura:** se paga al inicio y se descuenta del presupuesto de obra. La web deja de decir "sin costo adicional" e "incluido". Los trámites municipales se mencionan como gestión nuestra, sin hablar de precio. Los textos nuevos quedan ⚠️ para el visto bueno de Ariel.
- **Contacto:** WhatsApp y teléfono +56 9 4028 0657, y correo temporal oficina@claudiaarquitecta.cl. Son datos de Configuración del sitio y se cargan después del deploy, no en el código.
- **RUT** 77.897.204-2: va en el pie y en el JSON-LD (`taxID`).
- **Fotos:** se publican solo las obras con autorización escrita del dueño (un correo o un WhatsApp, guardado).
- **Pendiente:** el acceso al registrador de schobras.cl, para el dominio y para Google Workspace.

## 2026-10-23 (noche) — correo público y deploy

- **Correo público de contacto:** **oficina@schobras.cl**, en reemplazo del temporal oficina@claudiaarquitecta.cl. Está cargado en Configuración del sitio de producción. El usuario de Claudia para entrar al panel sigue siendo oficina@claudiaarquitecta.cl.
- **Primer deploy:** en `schobras-56c5d3fa8536.herokuapp.com`, sin dominio propio y sin indexar (`SEARCH_INDEXING`). Las fotos van a S3 (ADR-0006); hasta que esté, la subida queda apagada.
- **Pestaña "Cotiza tu proyecto" en el inicio:** aparece al llegar a Nosotros, no sobre la portada, y no se vuelve a ocultar.
