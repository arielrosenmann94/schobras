# ADR-0003 — Código en inglés, interfaz en español

Estado: active
Owner: Ariel Rosenmann / desarrollador
Última revisión: 2026-10-22
Versión del documento: 1.1.0
Tipo de cambio más reciente: minor
Notas del último cambio: excepción para nombres de herramientas MCP
Fuente de verdad: sí
Documentos relacionados: ../arquitectura.md
Objetivo: fijar el idioma del código y de la interfaz
Audiencia: arquitectura | desarrollo | agentes

---

## Contexto
webar, webdfchile y admindf escriben el código en inglés y la interfaz en español. El primer plan de schobras tenía nombres en español.

## Decisión (Ariel, 2026-10-22)
Modelos, campos, funciones, apps y nombres de URL en inglés (`Project`, `commune`, `projects:detail`). Textos visibles, mensajes, `verbose_name` y rutas públicas en español (`/proyectos/`, `/panel/ingresar/`). La app `proyectos` se renombra a `projects`.

Excepción: los nombres de las herramientas MCP de la v2.0 (`nuevo_plano`, `exportar_dxf`, `publicar_proyecto`, etc.) van en español, como en admindf. Son interfaz: Claude las elige conversando en español con la arquitecta. El código que las implementa sigue en inglés.

## Consecuencias
Consistencia entre repos de Ariel y con la futura API (v2.0). Los valores de choices se guardan en inglés con etiqueta en español.
