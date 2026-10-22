# ADR-0001 — PK UUID v7 en todos los modelos

Estado: active
Owner: Ariel Rosenmann / desarrollador
Última revisión: 2026-10-22
Versión del documento: 1.0.0
Tipo de cambio más reciente: major
Notas del último cambio: decisión inicial
Fuente de verdad: sí
Documentos relacionados: ../arquitectura.md
Objetivo: registrar por qué todos los modelos usan UUID v7
Audiencia: arquitectura | desarrollo | agentes

---

## Contexto
`instructivo/docs/07-appsec/uuid_e_idor.md` pide UUID v7 como PK en proyectos nuevos (evita IDs enumerables/IDOR y da IDs estables para APIs). La v2.0 expondrá una API para el conector MCP. Python 3.12 no trae `uuid.uuid7` (llega en 3.14).

## Decisión
`core.models.BaseModel` con `id = UUIDField(primary_key=True, default=uuid6.uuid7, editable=False)`. También `accounts.User`. Dependencia `uuid6` (mantenida), aprobada por Ariel el 2026-10-22. Las URLs públicas usan `slug`; el panel usa `<uuid:pk>`.

## Consecuencias
- IDs no enumerables en el panel y en la futura API.
- Al migrar a Python ≥ 3.14 se puede reemplazar por `uuid.uuid7` sin migración de datos.
