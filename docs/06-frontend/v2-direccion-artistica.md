# /v2 — Dirección artística "del plano a la obra"

Estado: draft (exploración; no reemplaza el inicio)
Owner: Ariel Rosenmann / desarrollador
Última revisión: 2026-10-25
Versión del documento: 1.1.0
Tipo de cambio más reciente: major
Notas del último cambio: primera exploración, a partir de la visión de experiencia web que trajo Ariel
Fuente de verdad: sí, para /v2
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

## 3 bis. Portada 3D (revisión de Ariel, 2026-10-25)

Ariel pidió un efecto "wow" sobre el pliegue, que fuera algo **distinto de la casa del Proceso** (el Proceso queda tal cual: "está perfecto") y **más industrial**, y que el scroll **cambie la información**, no solo la imagen.

- **Obra:** nave industrial de 24,00 × 16,00 m con marcos de acero (ejes A–G cada 4 m), correas, cerramientos antracita, cubierta clara, portón y ventana corrida, más un bloque de oficinas de dos pisos al frente, con fachada vidriada.
- **Recorrido:** la sección mide 2,2–2,6 pantallas y la portada queda fija. La cámara parte cenital, viendo el plano (el mismo de `core/v2/plan.svg.html`, que es el respaldo sin 3D), y baja a una vista en 3/4.
- **Etapas y servicio que muestra cada una** (textos existentes de Servicios; los nombres de las etapas quedan ⚠️):

| Avance | Etapa | Qué se arma | Servicio |
|---|---|---|---|
| 0 % | Proyecto | El plano | Proyecto de arquitectura a la medida. |
| 8 % | Fundaciones | Zapatas y radier | Especialidades: cálculo estructural, agua potable y alcantarillado, electricidad. |
| 22 % | Estructura | Marcos de acero uno por uno, correas y la estructura de las oficinas | Todos los sistemas constructivos: … estructuras metálicas. |
| 50 % | Cerramientos | Muros y cubierta | Cumplimiento normativo en sismorresistencia, resistencia al fuego y acondicionamiento térmico. |
| 78 % | Entrega | Fachada vidriada, portón y luces encendidas (bronce) | Llave en mano o con el nivel de terminaciones que necesites. |

- **Técnica:** three.js 0.186.1 compilado con esbuild en un solo archivo propio (`static/js/v2-hero3d.min.js`, unos 145 KB comprimido). Se carga con `import()` solo si hay WebGL, movimiento permitido y pantalla de 34em de alto o más. La cámara tiene inercia y, en computador, una órbita sutil con el mouse.
- Del prompt de referencia de Ariel (Three.js + GSAP, tema oscuro, GLB con Draco, pantalla de carga) se tomaron las etapas, la cámara dolly, el remate con luces y el indicador de avance. No se tomaron GSAP, el tema oscuro, el GLB ni la pantalla de carga (el plano SVG se ve al instante), ni las barras de scroll ocultas.
- Para recompilar: `cd frontend && npm ci && npm run build`.

## 4. Cómo está hecho

- Ruta `/v2/` (`core.views.home_v2`). La plantilla `core/home_v2.html` **hereda** de `core/home.html` y solo reemplaza los bloques `home_hero` y `home_process`. Así los textos no se duplican: los de las demás secciones salen del mismo archivo.
- `<meta name="robots" content="noindex, nofollow">`, fuera del sitemap. El menú lleva a `/v2/#…` y no saca al visitante de la versión.
- Dibujos: `core/templates/core/v2/plan.svg.html` y `elevation.svg.html`, con `aria-hidden`. El contenido accesible es la lista `<ol>` de pasos.
- `static/js/v2.js` (1,5 KB) escribe `--p` (de 0 a 1) según el avance por la lista. `static/css/v2.css` reparte `--p` en `--s1…--s6` y en las fases de la obra (`--found`, `--rebar`, `--walls`, `--roof`, `--glass`).
- **Sin JS o con `prefers-reduced-motion`:** `--p: 1`, la obra terminada, sin animación.
- Celular: el dibujo queda fijo arriba (sticky) y los pasos pasan por debajo. Desde 1024 px: los pasos a la izquierda y el dibujo fijo a la derecha.
- Verificado en Chrome: no hay desborde de 360 a 1440, la pestaña no tapa texto y no hay capas fuera de orden (core/tests/test_v2.py).

## 5. Cómo seguir por etapas (propuesta, Ariel decide)

1. **Revisar /v2 en pantalla** y decidir si el Proceso nuevo reemplaza al del inicio. Es un cambio de un bloque.
2. **Cuando estén las fotos (S3):** transición del dibujo a la foto real en el detalle de cada proyecto (la línea del plano se "rellena" con la foto). Solo con obras autorizadas.
3. **Portada viva:** la planta se dibuja una sola vez al cargar (los muros "se cortan" como en CAD), sin repetir el efecto en otras secciones.
4. **Las tres escalas:** un trazo por categoría (casa en parcela, local comercial, nave industrial con estructura metálica) en la misma línea de suelo, para Servicios o Proyectos.
5. **3D, solo si aporta:** si se quiere girar la casa, three.js autoalojado (sin CDN, CSP `'self'`) y cargado solo al llegar a esa sección, con medición de Lighthouse ≥ 90 antes de aceptarlo. Con la v2.0 (planos con IA, D3), el mismo modelo JSON de planta podría alimentar este dibujo con proyectos reales de Claudia.

## 6. Cuándo debe actualizarse

Cuando Ariel decida qué pasa de /v2 al inicio, o cuando se agregue una etapa de §5.
