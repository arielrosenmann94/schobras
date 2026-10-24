# Instrucciones para agentes — SCHOBRAS.CL

**IMPORTANTE — antes de tocar cualquier archivo de este repositorio, lee completo `.agents/CODING_AGENT_RULES.md`.** Es la fuente de verdad sobre qué se puede editar libremente, qué requiere plan previo y qué requiere aprobación humana explícita.

## Proyecto

`schobras` — web pública de **SCHOBRAS.CL** (Constructora Schonffeldt SpA, arquitectura + construcción en RM, Valparaíso y O'Higgins): sitio informativo + catálogo de proyectos administrable + backoffice propio (`/panel/`) para la dueña. Django 6 SSR en Heroku.

- Índice de documentación: @docs/README.md
- Diseño v1.0 (fuente de verdad del producto): @docs/2026-10-22-web-v1-diseno.md
- Plan de implementación v1.0: @docs/superpowers/plans/2026-10-22-web-v1.md
- Decisión de arquitectura v2.0 (no implementar todavía): @docs/2026-10-22-v2-decision-arquitectura.md

## Comandos

- Entorno: `python3.12 -m venv env_schobras && ./env_schobras/bin/pip install -r requirements.txt`
- Local: `./env_schobras/bin/python manage.py runserver` (usa `config.settings.local`)
- Tests: `./env_schobras/bin/python manage.py test`
- Definition of Done (correr antes de cada commit): ver @docs/09-qa-dod/definition-of-done.md
- Grafo: `graphify update .` después de cambiar código

## Convenciones (resumen; detalle en `.agents/CODING_AGENT_RULES.md`)

- **Código en inglés, interfaz y rutas públicas en español.**
- Todos los modelos heredan `core.models.BaseModel` (PK UUID v7 con `uuid6`, `created_at`, `updated_at`).
- **Toda escritura de negocio pasa por `projects/services.py`** (panel hoy, API/MCP en v2.0). Nunca lógica de negocio en vistas ni en el admin.
- Forms/ModelForms con `fields` explícito. PRG. CSP nativa sin `unsafe-inline`.
- CSS y JS propios, sin frameworks ni CDN. Sin `style="..."` en plantillas.
- Panel con CBV de Django.

## Prohibido (reglas duras heredadas de admindf)

1. **Nunca imprimir secretos de producción**: ni `heroku config`, `heroku config:get` (salvo `| wc -c`), `heroku releases:info`, `heroku pg:credentials`, `heroku run env`, `heroku run ... os.environ`. Si hace falta saber si existe una variable, `heroku config:get VAR | wc -c`, o preguntar a Ariel.
2. **Nunca escribir comentarios `{# ... #}` de más de una línea** en plantillas: Django los muestra como texto. Para comentarios largos usar `{% comment %}…{% endcomment %}` o `<!-- -->`. Después de editar una plantilla: `grep -n '{#' archivo.html` y confirmar que cada uno cierra en la misma línea.
3. **Nunca `git push` ni deploy.** Lo hace Ariel, con aprobación explícita en cada ocasión.
4. Nunca leer ni editar `.env*`.

## Commits

Conventional Commits `tipo(alcance): descripción` en imperativo, < 20 archivos por commit. Ver @.agents/CODING_AGENT_RULES.md §5.

## Cronómetro de trabajo (webar)

Siempre, **antes de la primera acción del trabajo** (antes de leer código o correr comandos): buscar una sesión de **webar** (`ListAgents`) y pedirle **iniciar** el cronómetro en schobras › Web informativa, **en la tarea que corresponde al tipo de trabajo**:

| Trabajo | Tarea en webar |
|---|---|
| Programar, corregir, QA, documentación | "Desarrollo" (#1058) |
| Preparar o hacer el despliegue (Heroku, GitHub, dominio, runbook) | "Deploy" (#1129) |

Si el trabajo cambia de tipo a mitad de camino, pedir stop del tramo actual e inicio en la otra tarea (nunca dos tramos abiertos). Al terminar, pedirle **detenerlo** (stop; pausa solo si se sigue enseguida). Si no hay ninguna sesión de webar, avisar a Ariel. Quién lo pide y el detalle: @docs/09-qa-dod/qa-circular-v1.md §Cronómetro.

## Advertencias específicas

- La clienta (Claudia Schonffeldt) no es técnica: el panel debe ser imposible de romper (confirmaciones, no borrar categorías con proyectos, sin acceso a configuración).
- Ningún modelo tiene campo de dirección (privacidad de los clientes de la constructora).
- El bronce `#B57949` sobre blanco no cumple contraste AA para texto normal: solo en líneas, íconos y texto ≥ 24 px.
- Las fotos van a Cloudinary en producción; en local, a `media/`.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
