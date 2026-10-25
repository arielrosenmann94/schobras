# Dirección artística "del plano a la obra" (ex /v2, hoy el inicio)

Estado: active (aprobada por Claudia el 2026-10-25; es el inicio en /)
Owner: Ariel Rosenmann / desarrollador
Última revisión: 2026-10-25
Versión del documento: 2.0.0
Tipo de cambio más reciente: major
Notas del último cambio: Claudia aprobó el diseño; pasa a ser el inicio (/v2/ redirige a /), la portada 3D es una casa en maqueta y se agrega /sch para elegir cómo se escribe la marca
Fuente de verdad: sí, para la portada 3D, el Proceso animado y /sch
Documentos relacionados: guia-visual.md, ../02-producto/textos-v1.md, ../2026-10-22-web-v1-diseno.md §4
Objetivo: registrar qué se tomó de la visión de experiencia web, qué no, qué se construyó en /v2 y cómo seguir por etapas
Audiencia: desarrollo | diseño | agentes

---

## 1. De dónde viene

Ariel trajo un texto de visión ("SCH Construcciones — Visión de experiencia web"): una web inmersiva, con escenas que evolucionan con el scroll, una vivienda que se construye, estructuras que aparecen y transiciones cinematográficas. Pidió explorarlo **solo en términos de diseño**: **nuestra información manda**.

| De la visión | Qué hicimos |
|---|---|
| Experiencia que se descubre con el movimiento, no animación decorativa | **Sí**: un único momento protagonista, en el que la obra se levanta a medida que se recorre el Proceso |
| Una vivienda que se construye progresivamente | **Sí**: es el centro de /v2 |
| "SCH Construcciones", gas, calderas, lavanderías industriales | **No.** La marca es SCHOBRAS.CL y los servicios son los de textos-v1.md (residencial, comercial e industrial, sin prometer especialidades que no ofrecemos) |
| 3D, WebGL, librerías de animación | **No por ahora**: SVG + CSS + 1,5 KB de JS propio. Ver §5 |
| Navegación, rendimiento, móvil y contacto intactos | **Sí**: mismo menú, misma pestaña "Cotiza tu proyecto" y mismo contenido |

## 2. Oportunidades que tenía el sitio

1. **El Proceso de 6 pasos ya era una narración:** del terreno a la obra. Faltaba que se *viera* avanzar. Es justo la promesa de la marca: diseñamos (plano) y construimos (obra), y la arquitectura se descuenta si construyes con nosotros.
2. **El lenguaje de plano ya existía** (cotas, ejes, muros, el isotipo de fierros). /v2 lo lleva de ornamento a contenido: el plano es literalmente un plano.
3. **Sin fotos de obras todavía** (S3 pendiente): un dibujo propio no depende de fotos y no expone casas de clientes.

## 3. El concepto

**Del plano a la obra.** La portada muestra la **planta** de una casa de 12,00 × 8,00 m, con ejes A–G, cotas en bronce y muros macizos. En el **Proceso**, la **elevación de esa misma casa** (mismos ejes y medidas) queda fija mientras pasan los pasos, y cada paso agrega su capa:

| Paso | Capa del dibujo |
|---|---|
| 01 Visita técnica | Terreno, estacas y la medida del terreno |
| 02 Presupuesto de especialidades | Ejes estructurales A–G y niveles ±0,00 · +2,60 · +5,60 |
| 03 Estudio y propuesta | El contorno de la casa se dibuja |
| 04 Ajustes en conjunto | Aparece y se va una alternativa (techo y ventana) |
| 05 Proyecto y presupuesto de obra | Cotas de altura y la fundación por debajo del suelo |
| 06 Construcción | Fundación (bronce), fierros que suben, muros que se levantan, techumbre y ventanas; las líneas de proyecto se apagan |

Todo lo demás (Nosotros, Por qué SCH OBRAS, Servicios, Proyectos, Zona y Contacto) queda **igual que en el inicio**: la audacia se gasta en un solo lugar.

**Tokens:** los de guia-visual.md, sin colores nuevos. El bronce es línea (cotas, fierros, fundación) y número de paso activo de 40 px o más. Open Sans, sin fuentes nuevas.

## 3 ter. Aprobación de Claudia e inicio (2026-10-25)

Claudia aprobó el diseño ("las animaciones me parecen súper") y Ariel lo puso como **web principal**:

- `/` usa la portada 3D y el Proceso animado. `/v2/` redirige con 301 a `/`. El inicio anterior (portada con el isotipo armándose y Proceso en planilla) y su CSS se borraron.
- Los archivos y clases conservan el prefijo `v2` (`v2.css`, `v2.js`, `v2-hero3d.min.js`, `.v2-hero`, `.v2-build`): es el nombre del diseño, no de una ruta.
- **Portada:** Claudia pidió "mayor terminación, aunque fuera una casa muy básica, que sea linda". Ariel eligió una **casa 3D bien terminada** en lugar de la nave industrial (ver la tabla de abajo, actualizada).
- **Textos:** sus correcciones están en `../02-producto/textos-v1.md` v1.2.0 (Nosotros, Especialidades, Soluciones industriales, Estudio y propuesta).

## 3 bis. Portada 3D (revisión de Ariel, 2026-10-25; obra cambiada por Claudia el mismo día)

> La primera versión fue una nave industrial de 24,00 × 16,00 m (commit 9b8cce5). Claudia pidió más terminación y se cambió por la casa de abajo; las etapas y los textos no cambiaron.

Ariel pidió un efecto "wow" sobre el pliegue, que fuera algo **distinto de la casa del Proceso** (el Proceso queda tal cual: "está perfecto") y **más industrial**, y que el scroll **cambie la información**, no solo la imagen.

- **Obra:** casa de un piso en L de 17,00 × 11,00 m, presentada como una **maqueta de arquitectura** sobre un tablero: volumen social blanco (11 × 7 m) con fachada vidriada y marcos antracita, ala de dormitorios (6 × 11 m) revestida en listones de madera (bronce), losas de techo con canto antracita, terraza de madera, piscina, camino de piedras y árboles de maqueta. Es distinta de la casa del Proceso (dos pisos, 12,00 m, en elevación).
- **Recorrido:** la sección mide 2,2–2,6 pantallas y la portada queda fija. La cámara parte cenital, viendo el plano (el mismo de `core/v2/plan.svg.html`, que es el respaldo sin 3D), y baja a una vista en 3/4.
- **Etapas y servicio que muestra cada una** (textos existentes de Servicios; los nombres de las etapas quedan ⚠️):

| Avance | Etapa | Qué se arma | Servicio |
|---|---|---|---|
| 0 % | Proyecto | El plano | Proyecto de arquitectura a la medida. |
| 5 % | Fundaciones | Cimientos corridos (visibles desde el 5 %, pedido de Ariel) y radier | Especialidades: cálculo estructural, agua potable y alcantarillado urbano y rural, electricidad bifásica y trifásica, y climatización. |
| 22 % | Estructura | Pilares uno por uno y las cadenas que los amarran | Todos los sistemas constructivos: … estructuras metálicas. |
| 50 % | Cerramientos | Muros con sus vanos y losas de techo que bajan | Cumplimiento normativo en sismorresistencia, resistencia al fuego y acondicionamiento térmico. |
| 78 % | Entrega | Vidrios y marcos, listones de madera, terraza, piscina, jardín y luces cálidas en el interior | Llave en mano o con el nivel de terminaciones que necesites. |

- **Técnica:** three.js 0.186.1 compilado con esbuild en un solo archivo propio (`static/js/v2-hero3d.min.js`, unos 143 KB comprimido). Reflejos de estudio con `RoomEnvironment` (incluido en three), mapeo de tonos neutro (respeta los colores de marca) y sombras suaves. Las piezas repetidas (listones, pilares, árboles) son mallas instanciadas que aparecen una tras otra. Se carga con `import()` solo si hay WebGL, movimiento permitido y pantalla de 34em de alto o más. La cámara tiene inercia y, en computador, una órbita sutil con el mouse.
- Del prompt de referencia de Ariel (Three.js + GSAP, tema oscuro, GLB con Draco, pantalla de carga) se tomaron las etapas, la cámara dolly, el remate con luces y el indicador de avance. No se tomaron GSAP, el tema oscuro, el GLB ni la pantalla de carga (el plano SVG se ve al instante), ni las barras de scroll ocultas.
- **Más terminación y realismo** (pedido de Claudia, 2026-10-25): techo de grava antracita con antepecho blanco, pasto que reemplaza la tierra en la entrega, piscina turquesa con reflejos y borde de cerámica, árboles de copas verdes en varios tonos con troncos café, dos reposeras en la terraza y líneas del plano con grosor real (2 px; `LineMaterial`). Las texturas (grava, pasto, agua) se dibujan en un canvas: sin archivos de imagen. El archivo compilado pasa a ~150 KB comprimido.
- **Imagen fija mientras carga** (pedido de Ariel, 2026-10-25: "que se vea altiro la nueva animación"): `static/img/portada-plano-{400,800,720,1440}.webp` es el primer cuadro de la escena, renderizado por el mismo código en 4:5. Se muestra con `cover` en el lugar de la escena y se precarga solo cuando aplica el 3D. La cámara del primer cuadro usa el mismo encuadre (`POSTER_ASPECT`), así el paso de la imagen al 3D no se nota. El plano SVG queda solo de respaldo (sin JS, movimiento reducido o sin WebGL). **Si cambia el primer cuadro de la escena, hay que regenerar las cuatro imágenes.**
- **Celular bajo o con letra grande** (Samsung de Claudia, 2026-10-25: la obra quedaba en una franja bajo el título): el encabezado ya no reserva el carril de la pestaña de WhatsApp (va a media altura) y bajo 21em queda solo el ícono del menú; en pantallas de hasta 46em de alto la portada fija se compacta (sin antetítulo, título y bajada más chicos). Las medidas en em siguen la letra del teléfono. Si con todo la obra tiene menos de max(140 px, 22 % del alto), `v2.js` no carga three.js y deja el plano fijo.
- Para recompilar: `cd frontend && npm ci && npm run build`.

## 4. Cómo está hecho

- Ruta `/` (`core.views.home`, plantilla `core/home.html`). Hasta el 2026-10-25 vivía en `/v2/` con su propia plantilla y `noindex`; hoy `/v2/` redirige a `/`.
- Dibujos: `core/templates/core/v2/plan.svg.html` (planta de la casa de la portada, respaldo sin 3D) y `elevation.svg.html` (casa del Proceso), con `aria-hidden`. El contenido accesible es la lista `<ol>` de pasos.
- `static/js/v2.js` (1,5 KB) escribe `--p` (de 0 a 1) según el avance por la lista. `static/css/v2.css` reparte `--p` en `--s1…--s6` y en las fases de la obra (`--found`, `--rebar`, `--walls`, `--roof`, `--glass`).
- **Sin JS o con `prefers-reduced-motion`:** `--p: 1`, la obra terminada, sin animación.
- Celular: el dibujo queda fijo arriba (sticky) y los pasos pasan por debajo. Desde 1024 px: los pasos a la izquierda y el dibujo fijo a la derecha.
- Verificado en Chrome: no hay desborde de 360 a 1440, la pestaña no tapa texto y no hay capas fuera de orden (core/tests/test_v2.py).

## 4 bis. Cómo se escribe la marca: /sch (2026-10-25)

"SCHOBRAS" escrito junto puede leerse "sobras". Ariel pidió una página para elegir cómo distinguir SCH de obras:

- `/sch/` (`core.views.brand_options`, plantilla `core/sch.html`): 12 opciones numeradas, cada una grande, al tamaño del encabezado y sobre antracita como en el pie. "Probar en el encabezado" (`static/js/sch.js`) la pone en la marca del encabezado de esa misma página, sin cambiar nada en la web.
- La opción 1 es la actual. La opción 2 es la propuesta de Claudia: **SCH** en mayúsculas y **obras** en minúsculas, en el bronce del logo.
- Sin indexar, fuera del menú y del sitemap. Las variantes están en `core.views.BRAND_OPTIONS` y `static/css/sch.css` (`.wm--N`).
- **Elegida: opción 4** (Claudia, 2026-10-25): `SCHobras.cl`, con SCH en bronce. Aplicada en `brand_name` (encabezado, pie, panel, páginas de error y «Por qué SCHobras») y en el texto plano de títulos, metas, JSON-LD y aria-label (ver `../02-producto/textos-v1.md`). El correo sigue con `email_brand` (sch en otro tono). `/sch/` queda como registro; se puede borrar.

## 5. Cómo seguir por etapas (propuesta, Ariel decide)

1. ~~Revisar /v2 en pantalla y decidir si reemplaza al inicio.~~ Hecho el 2026-10-25.
2. **Cuando estén las fotos (S3):** transición del dibujo a la foto real en el detalle de cada proyecto (la línea del plano se "rellena" con la foto). Solo con obras autorizadas.
3. **Portada viva:** la planta se dibuja una sola vez al cargar (los muros "se cortan" como en CAD), sin repetir el efecto en otras secciones.
4. **Las tres escalas:** un trazo por categoría (casa en parcela, local comercial, nave industrial con estructura metálica) en la misma línea de suelo, para Servicios o Proyectos.
5. **3D, solo si aporta:** si se quiere girar la casa, three.js autoalojado (sin CDN, CSP `'self'`) y cargado solo al llegar a esa sección, con medición de Lighthouse ≥ 90 antes de aceptarlo. Con la v2.0 (planos con IA, D3), el mismo modelo JSON de planta podría alimentar este dibujo con proyectos reales de Claudia.

## 6. Cuándo debe actualizarse

Cuando cambie la portada 3D o el Proceso, cuando se elija la forma de escribir la marca (§4 bis) o cuando se agregue una etapa de §5.
