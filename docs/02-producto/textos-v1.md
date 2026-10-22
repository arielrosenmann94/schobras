# Textos públicos v1.0 — SCHOBRAS.CL

Estado: active
Owner: Ariel Rosenmann / desarrollador
Última revisión: 2026-10-22
Versión del documento: 1.0.0
Tipo de cambio más reciente: major
Notas del último cambio: textos iniciales, adaptados del documento de la clienta y sus respuestas
Fuente de verdad: sí (texto exacto que va en la web)
Documentos relacionados: ../cliente/caracteristicas-pag-web.md, ../../respuestas-cliente-2026-10-22.md, ../2026-10-22-web-v1-diseno.md §5–6
Objetivo: fijar palabra por palabra los textos de la web para que el código no los invente
Audiencia: desarrollo | agentes

---

> Marcados ⚠️: pendientes de confirmación. Si cambian, se cambian **aquí** y luego en la plantilla.

## Metadatos

- Título inicio: `SCHOBRAS.CL | Arquitectura y construcción en RM, Valparaíso y O'Higgins`
- Descripción inicio: `Diseñamos y construimos proyectos residenciales, comerciales e industriales. Proyecto de arquitectura y trámites municipales sin costo adicional si construyes con nosotros.`
- Título detalle: `{título} en {comuna} | SCHOBRAS.CL`
- Título lista: `Proyectos | SCHOBRAS.CL`

## Menú

Nosotros · Servicios · Proceso · Proyectos (solo si hay proyectos publicados) · Contacto (solo si hay un canal configurado)

## Portada

- Antetítulo: `Arquitectura y construcción · Región Metropolitana · Valparaíso · O'Higgins`
- H1: `Diseñamos y construimos tu proyecto.` ⚠️ alternativa para Ariel: `Del plano a la obra, con un solo equipo.`
- Bajada: `Si construyes con nosotros, el proyecto de arquitectura y los trámites municipales van sin costo adicional.` ⚠️ pendiente de que Claudia confirme si se cobra y descuenta o nunca se cobra.
- Botón principal: `Conversemos tu proyecto` (solo si hay contacto)
- Botón secundario: `Ver proyectos` (solo si hay proyectos)

## 01 · Nosotros

Somos un grupo de profesionales apasionados por la excelencia, con más de 25 años de experiencia en el desarrollo y ejecución de proyectos residenciales, obras civiles y espacios comerciales.

Trabajamos con seriedad y rigor en cada etapa, con un trato cercano, transparente y personalizado. Combinamos la precisión técnica de la construcción con la funcionalidad y el diseño de la arquitectura, para entregar soluciones duraderas que agregan valor a nuestros clientes y su entorno.

**Visión**
Ser una constructora de referencia por la excelencia técnica de nuestras obras, su durabilidad y la confianza de nuestros clientes: el aliado ideal tanto para familias que buscan concretar su hogar como para empresas e instituciones que requieren infraestructura comercial y civil de alto rendimiento.

## 02 · Por qué SCHOBRAS

1. **Arquitectura y trámites sin costo adicional** (destacado) — Si ejecutas la construcción con nosotros, el proyecto de arquitectura y los trámites en la Dirección de Obras Municipales van incluidos. Continuidad y eficiencia desde el plano hasta la entrega.
2. **Escuchamos e interpretamos** — Entendemos en profundidad lo que necesitas y sueñas, y lo traducimos en un diseño a tu medida y en soluciones constructivas reales.
3. **Rigor técnico y normativo** — Todas nuestras obras cumplen la normativa vigente en sismorresistencia, resistencia al fuego y acondicionamiento térmico: edificaciones seguras, confortables y duraderas.

## 03 · Servicios

**Diseño y especialidades**
- Proyecto de arquitectura a la medida.
- Especialidades: cálculo estructural, agua potable y alcantarillado, electricidad.
- Gestión de permisos y trámites municipales.

**Construcción**
- Obra nueva desde cero, ampliaciones y remodelaciones.
- Edificación residencial, comercial e industrial.
- Llave en mano o con el nivel de terminaciones que necesites.

**Cómo construimos**
- Proyectos personalizados, no viviendas tipo: diseñados según tus necesidades y el emplazamiento de tu terreno.
- Todos los sistemas constructivos: albañilería, hormigón armado, madera, volcometal, paneles SIP y estructuras metálicas.
- Cumplimiento normativo en sismorresistencia, resistencia al fuego y acondicionamiento térmico.

## 04 · Proceso

1. **Visita técnica y entrevista** — Conocemos tu terreno y conversamos contigo para entender tus requerimientos y necesidades.
2. **Presupuesto de arquitectura y especialidades** — Te presentamos el presupuesto del proyecto de arquitectura y de las especialidades que correspondan (cálculo, agua, alcantarillado, electricidad).
3. **Estudio y propuesta** — Si lo apruebas, estudiamos tu caso y te presentamos una propuesta.
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
- Botón flotante: `aria-label="Escríbenos por WhatsApp"`
- Mensaje WhatsApp por defecto: `Hola, quiero conversar sobre un proyecto.`

## Pie

`SCHOBRAS.CL` · `Constructora Schonffeldt SpA` · `Región Metropolitana · Valparaíso · O'Higgins` · canales configurados · `© {año}`

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

## ⚠️ Pendiente de visto bueno de Ariel (QA vuelta 1)

Textos que ya están en el sitio o en el panel y no estaban en este documento (QA-1.14). No se cambiaron: quedan aquí para que Ariel los apruebe o los corrija en la revisión humana. Cuando los apruebe, se mueven a su sección y se borra esta marca.

### Ya publicados

| Dónde | Texto |
|---|---|
| Proyectos (lista): meta descripción | `Obras de arquitectura y construcción de SCHOBRAS.CL en la Región Metropolitana, Valparaíso y O'Higgins.` |
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
| 400 (envío rechazado, p. ej. más de 100 fotos de una vez): título de la pestaña | `Algo salió mal \| SCHOBRAS.CL` |
| 400: título | `Algo salió mal con el envío` |
| 400: texto | `Si subías fotos, sube de a menos.` |
| 400: botón | `Volver al inicio` |
| Panel, foto con demasiados megapíxeles (tope por formato desde la QA vuelta 2: 40 en JPG, 20 en PNG, 12 en WebP) | `La foto {nombre} tiene demasiados megapíxeles (máximo {40, 20 o 12}).` |
| Panel, categoría repetida (sin importar mayúsculas) | `Ya existe una categoría con ese nombre.` |
| Panel, año fuera de rango | `El año debe estar entre 1950 y {año actual + 2}.` |
