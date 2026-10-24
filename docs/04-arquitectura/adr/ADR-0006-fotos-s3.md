# ADR-0006 — Fotos en Amazon S3 (reemplaza a ADR-0002)

Estado: active (decidido; implementación pendiente)
Owner: Ariel Rosenmann / desarrollador
Última revisión: 2026-10-23
Versión del documento: 1.0.0
Tipo de cambio más reciente: major
Notas del último cambio: Ariel deja Cloudinary fuera y elige S3
Fuente de verdad: sí
Documentos relacionados: ADR-0002-cloudinary.md (reemplazado), ../arquitectura.md, ../../07-appsec/seguridad.md, ../../12-runbooks/deploy-heroku.md, ../../2026-10-22-v2-decision-arquitectura.md (D7)
Objetivo: registrar dónde se guardan las fotos de proyectos en producción
Audiencia: arquitectura | desarrollo | agentes

---

## Contexto
El disco de Heroku se borra en cada despliegue, así que las fotos necesitan almacenamiento externo. ADR-0002 eligió Cloudinary. El 2026-10-23 Ariel lo dejó fuera y eligió S3, el mismo patrón que iterap (boto3), que además es donde irán los planos de la v2.0 (D7).

El primer deploy (2026-10-23, `schobras-56c5d3fa8536.herokuapp.com`, link de muestra para Claudia) salió **sin almacenamiento**. Sin `CLOUDINARY_URL`, `PHOTO_UPLOADS_ENABLED=False`: el panel muestra "La subida de fotos se habilita muy pronto.", el admin no permite agregar fotos y la sección Proyectos queda oculta, porque no hay proyectos con foto.

## Decisión (Ariel, 2026-10-23)
- **`django-storages` + `boto3`** (dependencias aprobadas), con `STORAGES["default"]` en `storages.backends.s3.S3Storage`.
- **Región `sa-east-1`** (São Paulo, la más cercana a Chile).
- **Variantes WebP generadas con Pillow** al subir la foto, en reemplazo de las URL `f_auto,q_auto,w_N` de Cloudinary. Los filtros `variant` y `srcset` pasan a apuntar a esos archivos (400/800/1600, según guia-visual.md). La re-codificación y los topes actuales (≤ 2560 px, sin EXIF/GPS, topes de megapíxeles por formato) se mantienen.

## A definir al implementar [propuesta de Claude; Ariel decide]
- **Lectura pública:** las fotos de la web son públicas por naturaleza. La propuesta es un bucket propio de schobras con lectura pública solo del prefijo de fotos de proyectos (política de bucket, sin ACL por objeto) y caché larga (`Cache-Control: max-age=31536000, immutable`, con nombres únicos). Evitar las URL firmadas para las fotos públicas: caducan y rompen la caché y el LCP. CloudFront queda como mejora si el LCP lo pide.
- **CSP:** agregar el host del bucket (`https://<bucket>.s3.sa-east-1.amazonaws.com`) a `img-src` y sacar `https://res.cloudinary.com`.
- **Credenciales:** un usuario IAM solo para la web, con permisos mínimos sobre ese bucket (`s3:PutObject`, `s3:GetObject`, `s3:DeleteObject` sobre `arn:aws:s3:::<bucket>/*`). Las config vars `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_STORAGE_BUCKET_NAME` y `AWS_S3_REGION_NAME` las crea Ariel en su terminal; nunca se imprimen.
- **Cuenta:** a nombre de Claudia, pagada con la tarjeta de la empresa, igual que Heroku. Ariel opera con acceso delegado.
- **Interruptor:** `PHOTO_UPLOADS_ENABLED` pasa a depender de la configuración de S3 en vez de `CLOUDINARY_URL`. Cuando S3 esté en producción, se saca la rama de Cloudinary y las dependencias `cloudinary` y `django-cloudinary-storage`.
- **Planos de la v2.0:** en un bucket **privado y separado**, con URL firmadas (D7). Nunca en el bucket público de fotos.

## Consecuencias
- Hay que programar las variantes y su borrado (al borrar una foto, se borran todas sus variantes).
- Costo bajo de S3 y de transferencia, que paga la empresa. Hay que comunicárselo a Claudia junto con Heroku.
- Mientras no esté S3: no se pueden publicar proyectos en producción (D7-1 del QA: el botón Publicar lleva a un callejón sin salida si la editora entra al panel).
