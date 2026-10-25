# Documentación — SCHOBRAS.CL

Estado: active
Owner: Ariel Rosenmann / desarrollador
Última revisión: 2026-10-22
Versión del documento: 1.0.0
Tipo de cambio más reciente: major
Notas del último cambio: índice inicial con la documentación de la v1.0
Fuente de verdad: sí (índice)
Documentos relacionados: ../CLAUDE.md, ../.agents/CODING_AGENT_RULES.md
Objetivo: mapa de toda la documentación del proyecto y de qué documento manda en cada tema
Audiencia: desarrollo | agentes | arquitectura

---

## Fuentes de verdad por tema

| Tema | Documento | Estado |
|---|---|---|
| Producto v1.0 (qué se construye y por qué) | [2026-10-22-web-v1-diseno.md](2026-10-22-web-v1-diseno.md) | active |
| Plan de implementación v1.0 | [superpowers/plans/2026-10-22-web-v1.md](superpowers/plans/2026-10-22-web-v1.md) | active |
| Textos públicos de la web | [02-producto/textos-v1.md](02-producto/textos-v1.md) | active |
| Modelo de datos | [03-dominio/modelo-de-datos.md](03-dominio/modelo-de-datos.md) | active |
| Arquitectura | [04-arquitectura/arquitectura.md](04-arquitectura/arquitectura.md) | active |
| Decisiones (ADR) | [04-arquitectura/adr/](04-arquitectura/adr/) | active |
| Guía visual y accesibilidad | [06-frontend/guia-visual.md](06-frontend/guia-visual.md) | active |
| Dirección artística /v2 ("del plano a la obra") | [06-frontend/v2-direccion-artistica.md](06-frontend/v2-direccion-artistica.md) | draft |
| Seguridad y secretos | [07-appsec/seguridad.md](07-appsec/seguridad.md) | active |
| Definition of Done | [09-qa-dod/definition-of-done.md](09-qa-dod/definition-of-done.md) | active |
| Despliegue en Heroku | [12-runbooks/deploy-heroku.md](12-runbooks/deploy-heroku.md) | active |
| Reglas para agentes | [../.agents/CODING_AGENT_RULES.md](../.agents/CODING_AGENT_RULES.md) | active |
| Diseño v1.1 (presencia y confianza) | [2026-10-22-web-v1.1-diseno.md](2026-10-22-web-v1.1-diseno.md) | draft |
| Arquitectura v2.0 (decisiones D1–D8) | [2026-10-22-v2-decision-arquitectura.md](2026-10-22-v2-decision-arquitectura.md) | active |
| Diseño v2.0 (API, MCP schobras, MCP planos, fases) | [2026-10-22-v2-diseno.md](2026-10-22-v2-diseno.md) | draft |

## Insumos de la clienta (no editar)

- [cliente/caracteristicas-pag-web.md](cliente/caracteristicas-pag-web.md) — transcripción del documento de identidad de marca (original: `../características pág web.docx`).
- [../respuestas-cliente-2026-10-22.md](../respuestas-cliente-2026-10-22.md) — respuestas al cuestionario.
- [../respuestas-cliente-2026-10-23.md](../respuestas-cliente-2026-10-23.md) — respuestas a las preguntas pendientes de la v1.0 (oferta de arquitectura, contacto, permisos de fotos, RUT).
- [../decisiones-v1.md](../decisiones-v1.md) — bitácora de decisiones de Ariel.

## Versiones

| Versión | Alcance | Estado |
|---|---|---|
| v1.0 | Web informativa + catálogo de proyectos + panel | en desarrollo, entrega 2026-10-26 |
| v1.1 | Redes sociales, cifras, ubicación, equipo/testimonios, logo definitivo, panel PWA con ingreso por huella (passkeys) | diseñada (draft), fecha por definir |
| v2.0 | Conector MCP + motor de planos con Claude | diseñada (draft); requiere reunión con Claudia (§13) antes del spike F0 |

## Cuándo debe actualizarse

Al crear, mover o deprecar cualquier documento, y al cerrar cada versión.
