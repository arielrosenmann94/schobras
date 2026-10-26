# Textos públicos v1.0 — SCHobras.cl

Estado: active
Owner: Ariel Rosenmann / desarrollador
Última revisión: 2026-10-25
Versión del documento: 1.4.0
Tipo de cambio más reciente: minor
Notas del último cambio: pie con derechos reservados, política de privacidad y crédito de desarrollo; página /privacidad/
Fuente de verdad: sí (texto exacto que va en la web)
Documentos relacionados: ../cliente/caracteristicas-pag-web.md, ../../respuestas-cliente-2026-10-22.md, ../2026-10-22-web-v1-diseno.md §5–6
Objetivo: fijar palabra por palabra los textos de la web para que el código no los invente
Audiencia: desarrollo | agentes

---

> Marcados ⚠️: pendientes de confirmación. Si cambian, se cambian **aquí** y luego en la plantilla.

## Metadatos

- Título inicio: `SCHobras.cl | Arquitectura y construcción en RM, Valparaíso y O'Higgins`
- Descripción inicio: `Diseñamos y construimos proyectos residenciales, comerciales e industriales. Si construyes con nosotros, el proyecto de arquitectura se descuenta del presupuesto de obra.` ⚠️ (reescrita el 2026-10-23: la arquitectura se paga al inicio y se descuenta)
- Título detalle: `{título} en {comuna} | SCHobras.cl`
- Título lista: `Proyectos | SCHobras.cl`

## Marca (regla de Ariel, 2026-10-23)

- **Forma elegida por Claudia el 2026-10-25 (opción 4 de /sch):** `SCHobras.cl`. SCH en mayúsculas y obras en minúsculas, así no se lee "sobras". Sin el dominio: `SCHobras` (p. ej. «Por qué SCHobras»).
- **En texto visible**, `SCH` va además en bronce (clase `.brand__sch`) y `obras.cl` en el color del texto, con el mismo peso. En plantillas se escribe con la etiqueta `{% brand_name %}` (con dominio) o `{% brand_name domain=False %}` (sin dominio), nunca a mano. La clase `.brand-name` impide que un contexto en mayúsculas (`.label`) cambie la caja.
- En texto plano (title, metas, JSON-LD, aria-label, alt) va sin estilo, pero con la misma caja: `SCHobras.cl`.
- *Antes del 2026-10-25:* `SCHOBRAS.CL` y `SCH OBRAS`.

## Menú

Nosotros · Servicios · Proceso · Proyectos (solo si hay proyectos publicados) · Contacto (solo si hay un canal configurado)

## Portada

- Antetítulo: `Arquitectura y construcción · Región Metropolitana · Valparaíso · O'Higgins`
- H1: `Diseñamos y construimos tu proyecto.` ⚠️ alternativa para Ariel: `Del plano a la obra, con un solo equipo.`
- Bajada: `Si construyes con nosotros, el valor del proyecto de arquitectura se descuenta del presupuesto de la obra.` ⚠️ Reescrita el 2026-10-23. Claudia confirmó que la arquitectura se paga al inicio y se descuenta del presupuesto de obra; ya no se dice "sin costo" ni "incluido".
- Botón principal: `Conversemos tu proyecto` (solo si hay contacto)
- Botón secundario: `Ver proyectos` (solo si hay proyectos)

## 01 · Nosotros

Somos un grupo de profesionales apasionados por la excelencia, con más de 25 años de experiencia en el desarrollo y ejecución de proyectos residenciales, industriales y comerciales.

Trabajamos con seriedad y rigor en cada etapa, con un trato cercano, transparente y personalizado. Combinamos la precisión técnica de la construcción con la funcionalidad y el diseño de la arquitectura, para entregar soluciones duraderas que agregan valor a nuestros clientes y su entorno.

**Visión**
Ser una constructora de referencia por la excelencia técnica de nuestras obras, su durabilidad y la confianza de nuestros clientes: el aliado ideal tanto para familias que buscan concretar su hogar como para empresas e instituciones que requieren infraestructura comercial y civil de alto rendimiento.

## 02 · Por qué SCH OBRAS

1. **La arquitectura se descuenta de tu obra** (destacado) ⚠️ — Pagas el proyecto de arquitectura al inicio y, si ejecutas la construcción con nosotros, su valor se descuenta del presupuesto de obra. Además gestionamos los trámites en la Dirección de Obras Municipales: continuidad y eficiencia desde el plano hasta la entrega.
2. **Escuchamos e interpretamos** — Entendemos en profundidad lo que necesitas y sueñas, y lo traducimos en un diseño a tu medida y en soluciones constructivas reales.
3. **Rigor técnico y normativo** — Todas nuestras obras cumplen la normativa vigente en sismorresistencia, resistencia al fuego y acondicionamiento térmico: edificaciones seguras, confortables y duraderas.

## 03 · Servicios

**Diseño y especialidades**
- Proyecto de arquitectura a la medida.
- Especialidades: cálculo estructural, agua potable y alcantarillado urbano y rural, electricidad bifásica y trifásica, y climatización.
- Gestión de permisos y trámites municipales.

**Construcción**
- Obra nueva desde cero, ampliaciones y remodelaciones.
- Edificación residencial, comercial e industrial.
- Soluciones industriales: tratamiento de aguas, alcantarillado, electricidad y climatización para cada obra.
- Llave en mano o con el nivel de terminaciones que necesites.

**Cómo construimos**
- Proyectos personalizados, no viviendas tipo: diseñados según tus necesidades y el emplazamiento de tu terreno.
- Todos los sistemas constructivos: albañilería, hormigón armado, madera, volcometal, paneles SIP y estructuras metálicas.
- Cumplimiento normativo en sismorresistencia, resistencia al fuego y acondicionamiento térmico.

## 04 · Proceso

1. **Visita técnica y entrevista** — Conocemos tu terreno y conversamos contigo para entender tus requerimientos y necesidades.
2. **Presupuesto de arquitectura y especialidades** — Te presentamos el presupuesto del proyecto de arquitectura y de las especialidades que correspondan (cálculo, agua, alcantarillado, electricidad y climatización).
3. **Estudio y propuesta** — Si lo apruebas, estudiamos tu caso en relación con la normativa vigente y tus necesidades, y te presentamos una propuesta.
4. **Ajustes en conjunto** — Incorporamos tus correcciones y nuestras sugerencias hasta llegar a la versión final.
5. **Proyecto y presupuesto de obra** — Te entregamos el proyecto de arquitectura junto con el presupuesto de construcción.
6. **Construcción con descuento del proyecto** — Si construyes con nosotros, el valor del proyecto de arquitectura se descuenta del presupuesto de la obra.

## 05 · Zona de trabajo

Región Metropolitana · Región de Valparaíso · Región de O'Higgins

## Proyectos

- Sección portada: `Proyectos` + enlace `Ver todos los proyectos`.
- Lista vacía: `Pronto publicaremos nuestras obras.`
- Filtro: `Todos` + nombres de categorías activas con proyectos.
- Cierre del detalle: `¿Tienes un proyecto parecido? Conversemos.`
- Mensaje WhatsApp del detalle: `Hola, vi el proyecto {título} y quiero conversar uno parecido.`

## Contacto

- Título: `¿Tienes un proyecto en mente?`
- Texto: `Cuéntanos qué quieres construir y conversemos cómo hacerlo realidad.`
- Etiquetas: `WhatsApp`, `Teléfono`, `Correo`
- Pestaña lateral (WhatsApp, borde derecho, solo si hay WhatsApp válido): texto `Cotiza tu proyecto` ⚠️ · `aria-label="Cotiza tu proyecto por WhatsApp"`
- Mensaje WhatsApp por defecto: `Hola, quiero conversar sobre un proyecto.`

## Pie

`SCHobras.cl` · `Constructora Schonffeldt SpA` · `RUT 77.897.204-2` · `Región Metropolitana · Valparaíso · O'Higgins` · canales configurados

Última línea (pedido de Ariel, 2026-10-25):
- `© {año} Constructora Schonffeldt SpA. Todos los derechos reservados.` + enlace `Política de privacidad` (→ /privacidad/)
- `Desarrollado por arielrosenmann.com` (enlace a https://arielrosenmann.com/, pestaña nueva)

## Política de privacidad (/privacidad/)

Pedido de Ariel (2026-10-25): el WhatsApp es solo para cotizar y consultar por proyectos; los datos no se comparten y se usan solo para la comunicación comercial del proyecto consultado. ⚠️ Texto base: revisarlo antes de que la web tenga formularios o analítica (v1.1+), que obligan a ampliarlo (CODING_AGENT_RULES §8).

- Título: `Política de privacidad`
- Bajada: `Cómo usamos los datos que nos entregas cuando nos contactas.`
- **Quién es responsable:** `Constructora Schonffeldt SpA, RUT 77.897.204-2, dueña de SCHobras.cl.`
- **Qué datos recibimos:** `Esta web no tiene formularios ni registra a quienes la visitan: no usamos cookies de seguimiento ni herramientas de analítica. Solo recibimos los datos que tú nos envías al escribirnos o llamarnos: tu nombre, tu número o correo y lo que nos cuentes de tu proyecto.`
- **Para qué los usamos:** `El contacto por WhatsApp es exclusivo para cotizar y consultar por proyectos de arquitectura y construcción. Los usamos solo para la comunicación comercial sobre el proyecto que consultaste.`
- **Con quién los compartimos:** `No compartimos tus datos con nadie. Los mensajes pasan por el servicio que elijas para escribirnos (WhatsApp, teléfono o correo), que tiene su propia política de privacidad.`
- **Tus derechos:** `Puedes pedirnos en cualquier momento saber qué datos tuyos tenemos, corregirlos o borrarlos, escribiendo a {correo}.` (sin correo configurado: `escribiéndonos por WhatsApp`)
- `Última actualización: 25 de octubre de 2026.`

## 404

- Título: `Esta página no existe`
- Texto: `Puede que el enlace esté mal escrito o que el proyecto ya no esté publicado.`
- Botón: `Volver al inicio`

## Panel (mensajes)

| Situación | Texto |
|---|---|
| Publicar sin fotos | `Agrega al menos una foto antes de publicar.` |
| Borrar categoría con proyectos | `Esta categoría tiene proyectos. Puedes desactivarla en vez de eliminarla.` |
| Foto > 15 MB | `La foto {nombre} pesa más de 15 MB.` |
| Formato no soportado | `Formato no soportado: sube fotos JPG, PNG o WebP.` |
| Aviso al subir fotos | `Sube solo fotos de obras que el dueño autorizó a publicar. No incluyas números de casa ni patentes.` |
| WhatsApp inválido | `Número de WhatsApp no válido. Ejemplo: +56 9 1234 5678` |
| Bloqueo por intentos | `Demasiados intentos. Vuelve a intentarlo en 30 minutos.` |
| Login fallido | `Correo o contraseña incorrectos.` |
| Subida de fotos apagada (producción sin almacenamiento, hasta S3) ⚠️ | `La subida de fotos se habilita muy pronto.` |

## ⚠️ Pendiente de visto bueno de Ariel (QA vueltas 1 y 2)

Textos que ya están en el sitio o en el panel y no estaban en este documento (QA-1.14). No se cambiaron: quedan aquí para que Ariel los apruebe o los corrija en la revisión humana. Cuando los apruebe, se mueven a su sección y se borra esta marca.

### Ya publicados

| Dónde | Texto |
|---|---|
| Proyectos (lista): meta descripción | `Obras de arquitectura y construcción de SCHobras.cl en la Región Metropolitana, Valparaíso y O'Higgins.` |
| Proyecto (detalle): botón de cierre con WhatsApp | `Escríbenos por WhatsApp` |
| Proyecto (detalle): botón de cierre sin WhatsApp, con teléfono | `Llámanos al {teléfono}` |
| Proyecto (detalle): botón de cierre solo con correo | `Escríbenos a {correo}` |
| 403: título | `No tienes acceso a esta página` |
| 403: texto | `Esta sección es solo para quien administra el sitio.` |
| 403: botón | `Volver al panel` (con sesión) / `Volver al inicio` (sin sesión) |
| 500: título | `Algo falló de nuestro lado` |
| 500: texto | `No pudimos cargar esta página. Vuelve a intentarlo en unos minutos.` |

### Nuevos en la QA vuelta 1

| Dónde | Texto |
|---|---|
| 400 (solicitud rechazada, p. ej. Host inválido o más de 100 fotos de una vez): título de la pestaña | `Algo salió mal \| SCHobras.cl` |
| 400: título (genérico desde la QA vuelta 2; antes `Algo salió mal con el envío`) | `No pudimos procesar esta solicitud` |
| 400: texto (genérico desde la QA vuelta 2; antes `Si subías fotos, sube de a menos.`) | `Vuelve atrás e inténtalo de nuevo.` |
| 400: botón | `Volver al inicio` |
| Panel, foto con demasiados megapíxeles (tope por formato desde la QA vuelta 2: 40 en JPG, 20 en PNG, 12 en WebP) | `La foto {nombre} tiene demasiados megapíxeles (máximo {40, 20 o 12}).` |
| Panel, categoría repetida (sin importar mayúsculas) | `Ya existe una categoría con ese nombre.` |
| Panel, año fuera de rango | `El año debe estar entre 1950 y {año actual + 2}.` |

### Nuevos en la QA vuelta 2

| Dónde | Texto |
|---|---|
| Página caducada (fallo de CSRF en el panel): título de la pestaña | `La página caducó \| SCHobras.cl` |
| Página caducada: título | `La página caducó` |
| Página caducada: texto | `Por seguridad, el formulario venció. Vuelve al panel e inténtalo de nuevo.` |
| Página caducada: botón | `Volver al panel` |
| Proyecto (detalle): nombre accesible de cada miniatura (lector de pantalla) | `Ver foto {n} de {total}` |
| 403 (web y panel): título de la pestaña | `No tienes acceso \| SCHobras.cl` |

### Nuevos con el diseño "del plano a la obra" (ex /v2, inicio desde el 2026-10-25)

| Dónde | Texto |
|---|---|
| Inicio, portada 3D: indicador de avance mientras se arma la casa | `Avance de obra {0–100} %` |
| Inicio, portada 3D: aviso sobre el render fotorrealista del final (la casa no existe) | `Imagen referencial` |
| /sch (página interna, sin indexar): título | `Cómo escribimos SCHOBRAS` |
| /sch: botón de cada opción | `Probar en el encabezado` |
| /sch: nombres y descripciones de las 12 opciones | en `core.views.BRAND_OPTIONS` (página de trabajo; no es texto público) |

### Nuevos en la revisión de Ariel (ronda 1)

| Dónde | Texto |
|---|---|
| Pestaña lateral de WhatsApp (reemplaza al botón flotante): texto visible | `Cotiza tu proyecto` |
| Pestaña lateral: nombre accesible (empieza con el texto visible) | `Cotiza tu proyecto por WhatsApp` |
