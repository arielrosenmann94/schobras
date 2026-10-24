# ADR-0002 — Fotos en Cloudinary (reemplazado)

> **Reemplazado el 2026-10-23 por [ADR-0006](ADR-0006-fotos-s3.md):** Ariel dejó Cloudinary fuera; las fotos irán a S3. El código mantiene la rama de Cloudinary hasta que S3 esté implementado.

Estado: superseded por ADR-0006 (S3), 2026-10-23
Owner: Ariel Rosenmann / desarrollador
Última revisión: 2026-10-22
Versión del documento: 1.0.0
Tipo de cambio más reciente: major
Notas del último cambio: decisión inicial
Fuente de verdad: sí
Documentos relacionados: ../arquitectura.md
Objetivo: registrar dónde y cómo se guardan las fotos de proyectos
Audiencia: arquitectura | desarrollo | agentes

---

## Contexto
El disco de Heroku se borra en cada despliegue. La velocidad de la web depende sobre todo del peso de las fotos. Ariel ya usa Cloudinary en webar con Django 6.

## Decisión
Add-on `cloudinary:starter` de Heroku, **en la cuenta de Claudia** (pagada con la tarjeta de la empresa). En producción `STORAGES["default"] = cloudinary_storage.storage.MediaCloudinaryStorage`, configurado por `CLOUDINARY_URL`. Las plantillas piden variantes con `f_auto,q_auto,w_N` (filtro `variant`) y `srcset` 400/800/1600.

## Consecuencias / riesgos
- `django-cloudinary-storage==0.3.0` tiene poco mantenimiento; funciona con Django 6 (webar en producción). Alternativa si se rompe: `django-storages` + S3.
- Los planos de la v2.0 **no** van a Cloudinary (son privados): S3 privado (ver decisión v2.0 D7).
