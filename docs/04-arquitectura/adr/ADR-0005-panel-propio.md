# ADR-0005 — Backoffice propio en vez del admin de Django

Estado: active
Owner: Ariel Rosenmann / desarrollador
Última revisión: 2026-10-22
Versión del documento: 1.0.0
Tipo de cambio más reciente: major
Notas del último cambio: decisión inicial
Fuente de verdad: sí
Documentos relacionados: ../arquitectura.md
Objetivo: registrar por qué la clienta no usa el admin de Django
Audiencia: arquitectura | desarrollo | agentes

---

## Contexto
La dueña no es técnica. El admin de Django expone demasiado y no está pensado para subir fotos desde el celular.

## Decisión (Ariel, 2026-10-22)
Backoffice `/panel/` hecho a medida: español, botones grandes (≥ 48 px), usable desde el celular, con protecciones (confirmar borrados, no borrar categorías con proyectos, sin acceso a configuración para la editora). Login con django-axes. El admin de Django queda solo para Ariel en una URL no predecible (`ADMIN_URL`) y como respaldo de carga mientras el panel no esté listo.

## Consecuencias
Más trabajo que el admin, pero la clienta puede operar sola. Prioridad del lunes: si falta tiempo, el panel se corre y Ariel carga por el admin.
