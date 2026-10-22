# ADR-0004 — services.py como única puerta de escritura

Estado: active
Owner: Ariel Rosenmann / desarrollador
Última revisión: 2026-10-22
Versión del documento: 1.0.0
Tipo de cambio más reciente: major
Notas del último cambio: decisión inicial
Fuente de verdad: sí
Documentos relacionados: ../arquitectura.md
Objetivo: asegurar que las reglas de negocio vivan en un solo lugar
Audiencia: arquitectura | desarrollo | agentes

---

## Contexto
Hoy escriben datos el panel y el admin de Django; en la v2.0 escribirá también la API del conector MCP. En admindf, cuando la UI y el conector implementaron la misma regla por separado, divergieron (ver skill `conector-mcp-admindf`, "regla de negocio compartida").

## Decisión
Toda operación de negocio (publicar, despublicar, agregar fotos, portada, mover, borrar foto) vive en `projects/services.py`. Vistas, acciones del admin y la futura API solo llaman al servicio. Los forms validan formato; los servicios validan reglas.

## Consecuencias
Las reglas se prueban una vez (`projects/tests/test_services.py`) y el conector v2.0 se construye envolviendo servicios ya probados.
