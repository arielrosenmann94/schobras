# SCHOBRAS.CL — Diseño de la web informativa v1.0

**Fecha:** 2026-10-22 · **Autor:** Ariel Rosenmann (con Claude) · **Estado:** borrador para aprobación

Fuentes: `características pág web.docx` (identidad y textos de la clienta), [respuestas-cliente-2026-10-22.md](../respuestas-cliente-2026-10-22.md), [decisiones-v1.md](../decisiones-v1.md).

Convención: lo marcado **[decisión de Claude]** no lo dijo ni Ariel ni la clienta; es una propuesta razonable que Ariel puede cambiar.

---

## 1. Qué es y por qué

Constructora Schonffeldt SpA (marca **SCHOBRAS.CL**) diseña y construye: proyecto de arquitectura + construcción, por eso "obras". La dueña es Claudia Schonffeldt, arquitecta. Hoy no tienen web ni redes.

La v1.0 es una **web informativa** que presenta a la empresa como una constructora seria, técnica y cercana, y lleva al visitante a contactarlos. Además deja instalado desde el día uno un **catálogo de proyectos administrable** para que Claudia vaya subiendo obras sin depender del programador.

Es la base de una v2.0 (plataforma con Claude/MCP para gestionar la empresa y generar planos con IA), que se diseña por separado. La v1 no debe cerrarle la puerta: Django con modelos limpios.

**Plazo: entrega a la clienta el lunes 26 de octubre de 2026** (comprometido por correo). Todo lo que no cabe va a v1.1.

**Costos:** el desarrollo no tiene costo para la clienta (no se menciona). Ella paga los servicios externos: Google Workspace y Heroku (dos aplicaciones: la web y el backend).

**Cuentas:** Heroku y Cloudinary se crean a nombre de Claudia, pagadas con la tarjeta de la empresa; Ariel recibe acceso para operar (decidido por Ariel, 2026-10-22).

**Prioridad para el lunes** (decidido por Ariel): la web pública informativa primero; el panel después. Se espera alcanzar todo, pero si algo se atrasa, el panel es lo que se corre, y mientras tanto Ariel carga proyectos.

## 2. Objetivos, no-objetivos, anti-objetivos

**Objetivos**
- Que un visitante entienda en segundos qué hacen (arquitectura + construcción), dónde (RM, Valparaíso, O'Higgins) y su diferencial (proyecto de arquitectura y trámites municipales gratis si construye con ellos).
- Que se vea como arquitectura: limpia, minimalista, moderna, con contraste fuerte de escalas. "Como el muro de una casa piloto de las mejores."
- Que sea **rápida**.
- Que Claudia pueda cargar proyectos y categorías desde un **backoffice propio** sin saber de tecnología.

**No-objetivos de v1.0** (quedan fuera explícitamente)
- Formulario de contacto (la clienta no lo quiere por ahora).
- Redes sociales → **v1.1**.
- Cifras (obras realizadas, m² construidos) → **v1.1**.
- Foto o video de portada (v1.0 no lleva; la portada es tipográfica/geométrica).
- Equipo / fotos del equipo (la clienta aún no lo define).
- Testimonios (no hay todavía).
- Misión (la clienta la descartó: demasiado texto junto a Quiénes Somos y Visión).
- Dirección física, mapa, ficha de Google Maps, horario de atención (no se publican; dirección se preguntará después).
- Eslogan propio de la clienta (por ahora no tiene; ver §6).
- Textos de la web editables desde el panel (los textos van en plantillas).
- Formulario de contacto, chat, blog, multi-idioma, analítica.
- Todo lo de v2.0 (IA, MCP, planos).

**Anti-objetivos** (sería un fracaso aunque funcione)
- Que parezca una plantilla genérica de WordPress o de "constructora".
- Que cargue lenta o pesada en el celular.
- Que Claudia se pierda en el panel o pueda romper algo importante.
- Publicar la dirección de la casa de un cliente.
- Prometer servicios, años o cifras que la empresa no puede respaldar (los "25 años" son de los profesionales, no de la empresa).

## 3. Restricciones

- **Stack:** Django (decisión de Ariel), alineado con iterap y admindf (revisados 2026-10-22):
  - Python 3.12, **Django 6.0.x**, PostgreSQL con `psycopg[binary]` 3 y `dj-database-url`, `python-decouple` para variables de entorno, settings separados `base` / `production` (como iterap), `gunicorn`, `whitenoise` para estáticos, despliegue en **Heroku** con `Procfile` (`release`: migrate; Heroku corre collectstatic en el build). Versiones fijadas en `requirements.txt`.
  - **Fotos:** el disco de Heroku se borra en cada despliegue, así que las fotos necesitan almacenamiento externo. [decisión de Claude] **Cloudinary** (ya usado en webar): entrega cada foto redimensionada y en WebP/AVIF automáticamente, que es lo que más pesa en la velocidad. Alternativa: S3 con `boto3` como en iterap, generando los tamaños con Pillow.
  - Pensando en v2.0: iterap ya tiene un servidor MCP (`mcp_server_iterap.py`, paquete `mcp`) y admindf su conector; la v1 no lo incluye, pero los modelos deben quedar listos para exponerlos igual.
- **Dominio:** schobras.cl (titular Claudia Schonffeldt, registrador Registrar.eu). `www.schobras.cl` redirige a `schobras.cl` [decisión de Claude]. HTTPS obligatorio.
- **Identidad de marca** (documento de la clienta):
  - Gris antracita `#2C3539` — principal: estructuras, textos, logotipo.
  - Roble cálido / bronce `#B57949` — acento: detalles, isotipo, llamados de atención.
  - Gris piedra / cemento `#A9ABB6` — fondos de tarjetas, viñetas.
  - Blanco `#FFFFFF` — fondo.
  - Tipografía: **Open Sans** (semibold/medium para subtítulos y enlaces, regular para texto), autoalojada. El logotipo usa Copperplate Gothic Light pero va **como imagen**, nunca como fuente web (licencia; aprobado por la clienta).
- **Logo:** la clienta lo envía después; probablemente haya que retocarlo con IA al final. Hasta entonces se usa el isotipo del documento (edificio con fierros, PNG 191×207) + la palabra SCHOBRAS en Open Sans semibold, mayúsculas, con espaciado amplio [decisión de Claude]. Reemplazar el logo debe ser cambiar un archivo.
- **Rendimiento:** sin framework JS; HTML renderizado por Django; JS propio mínimo (objetivo < 20 KB) y CSS propio. Objetivo Lighthouse móvil ≥ 90 en rendimiento y accesibilidad, LCP < 2,5 s [decisión de Claude].
- **Animaciones:** solo CSS/IntersectionObserver, y desactivadas con `prefers-reduced-motion`.

## 4. Dirección visual

Lo que pidió la clienta: diseño limpio, minimalista, "altos y bajos" en relación de tamaño, que se vea arquitectura de obras, efectos muy modernos pero minimalistas, como construcciones limpias.

Traducido a reglas [decisión de Claude, el constructor puede refinar]:
- **Contraste de escala:** titulares muy grandes (display, antracita) junto a textos pequeños y aireados; números de sección grandes en bronce.
- **Lenguaje de plano:** líneas finas tipo cota/grilla de arquitectura, ejes visibles, mucho blanco. El bronce se usa poco y con intención (líneas, números, botón principal).
- **Planos de material:** bloques de color sólido (antracita, cemento) como muros que estructuran la página.
- **Movimiento:** revelados al hacer scroll que "levantan" bloques como muros (clip-path / translate), líneas que se dibujan, el isotipo de la portada armándose con sus verticales ("fierros"). Sutil, rápido, una vez.
- **Portada sin foto:** composición tipográfica + geométrica con el isotipo.

## 5. Estructura del sitio

Menú: Nosotros · Servicios · Proceso · Proyectos · Contacto. En celular, menú de pantalla completa.

### 5.1 Inicio (`/`) — una página larga con anclas
1. **Portada:** nombre, frase principal (ver §6), botón principal "Conversemos tu proyecto" (→ contacto) y secundario "Ver proyectos" (si hay proyectos publicados).
2. **Nosotros:** texto "Quiénes somos" + **Visión** (sin Misión).
3. **Por qué SCHOBRAS:** los tres pilares de la propuesta de valor. El primero, *proyecto de arquitectura y trámites municipales sin costo si construyes con nosotros*, es el protagonista visual.
4. **Servicios:**
   - Diseño de arquitectura y especialidades: cálculo estructural, sanitarios (agua y alcantarillado), eléctricos.
   - Construcción: obra nueva desde cero, ampliaciones y remodelaciones.
   - Edificación residencial, comercial e industrial.
   - Proyectos personalizados, no viviendas tipo: según las necesidades del cliente y el emplazamiento del terreno.
   - Llave en mano o con el nivel de terminaciones que el cliente necesite.
   - Todos los sistemas constructivos: albañilería, hormigón armado, madera, volcometal, paneles SIP y estructuras metálicas.
   - Cumplimiento normativo: sismorresistencia, resistencia al fuego, acondicionamiento térmico.
5. **Proceso** (6 pasos, de la respuesta de la clienta):
   1. Visita técnica y entrevista para conocer tus requerimientos.
   2. Presupuesto del proyecto de arquitectura y especialidades.
   3. Estudio y propuesta.
   4. Correcciones y sugerencias en conjunto.
   5. Proyecto de arquitectura + presupuesto de construcción.
   6. Si construyes con nosotros, el proyecto de arquitectura se descuenta del presupuesto de obra.
6. **Proyectos destacados:** hasta 6 proyectos marcados como destacados. La sección **no aparece** si no hay proyectos publicados [decisión de Claude].
7. **Zona de trabajo:** Región Metropolitana, Región de Valparaíso, Región de O'Higgins.
8. **Contacto:** bloque final con llamado a la acción. Muestra WhatsApp, teléfono y correo **solo si están configurados** (ver §7.3).
9. **Pie:** logo, "Constructora Schonffeldt SpA", zona de trabajo, contacto, año. Sin redes en v1.0. RUT no se muestra hasta tenerlo [decisión de Claude].

### 5.2 Proyectos (`/proyectos/`)
- Grilla de proyectos publicados, más recientes o por orden manual primero.
- Filtro por categoría con enlaces del servidor (`/proyectos/?categoria=residencial` o `/proyectos/residencial/`, a criterio del constructor), sin JS.
- Si no hay proyectos publicados, el enlace "Proyectos" desaparece del menú y la URL muestra un mensaje sobrio de "Pronto publicaremos nuestras obras" [decisión de Claude].

### 5.3 Detalle de proyecto (`/proyectos/<slug>/`)
- Foto de portada grande, ficha (categoría, tipo de intervención, comuna y región, sistemas constructivos, m², año: solo los que tengan valor), descripción y galería con visor a pantalla completa (JS mínimo, sin librería pesada).
- Llamado final: "¿Tienes un proyecto parecido? Conversemos."

### 5.4 Otros
- Página 404 con la misma identidad.
- `sitemap.xml`, `robots.txt`, metadatos y Open Graph por página, JSON-LD `GeneralContractor` con `areaServed` (3 regiones) y **sin dirección**.
- Favicon a partir del isotipo.

## 6. Contenido

- Los textos base son los del documento de la clienta (Quiénes somos, Visión, Propuesta de valor). El constructor puede acortarlos y ajustarlos para web manteniendo el sentido; la versión final la revisa Ariel.
- "Más de 25 años" siempre referido a la **experiencia de los profesionales**, nunca a la empresa.
- **Frase de portada:** la clienta no tiene eslogan. [decisión de Claude] El constructor propone una frase centrada en "diseñamos y construimos" + el diferencial de arquitectura sin costo; Ariel elige.
- **Público principal de la portada:** [decisión de Claude] personas y familias que quieren construir, ampliar o remodelar su casa (el documento parte con proyectos residenciales y el diferencial de arquitectura gratis les habla directo). Lo comercial e industrial aparece en Servicios y en las categorías.

## 7. Datos y backoffice

### 7.1 Modelos
**Categoría de proyecto** (creadas desde el panel, no en el código)
- nombre, slug (automático), orden, activa.
- Carga inicial: Residencial, Comercial, Industrial.

**Proyecto**
- título*, slug (automático), categoría*.
- tipo de intervención*: obra nueva / ampliación / remodelación.
- comuna*, región* (Metropolitana / Valparaíso / O'Higgins).
- sistemas constructivos (varios): albañilería, hormigón armado, madera, volcometal, paneles SIP, estructuras metálicas.
- superficie m² (opcional), año (opcional), descripción (opcional).
- estado: borrador / publicado. Para publicar se exige al menos una foto.
- destacado en portada (sí/no), orden manual.
- **No existe campo de dirección.** A propósito.

**Foto de proyecto**
- proyecto, imagen (Cloudinary), orden, es portada, texto alternativo (si se deja vacío, se usa el título del proyecto).
- tipo (opcional): obra terminada / en proceso / render.

**Configuración del sitio** (registro único)
- número de WhatsApp, teléfono visible, correo de contacto, mensaje prellenado de WhatsApp.

### 7.2 Backoffice (`/panel/`)
Hecho a medida, **no** el admin de Django. En español, botones grandes, usable desde el celular (Claudia probablemente sube fotos desde el teléfono).

| Usuario | Rol | Puede |
|---|---|---|
| Claudia Schonffeldt — oficina@claudiaarquitecta.cl | Editora (permisos bajos, no es tecnológica) | Crear, editar, publicar y despublicar proyectos; subir varias fotos a la vez, ordenarlas y elegir la portada; marcar destacados; crear y editar categorías; botón "Ver en la web" |
| Ariel Rosenmann — hola@arielrosenmann.com | Administrador | Todo lo anterior + Configuración del sitio + usuarios + admin de Django para emergencias |

Protecciones para la editora [decisión de Claude]:
- No puede borrar una categoría que tenga proyectos (solo desactivarla).
- Borrar un proyecto o una foto pide confirmación.
- No ve la configuración del sitio ni los usuarios.
- Al subir fotos, el panel muestra el recordatorio: "Sube solo fotos de obras que el dueño autorizó a publicar. No incluyas números de casa ni patentes."
- Recuperar contraseña: en v1.0 lo hace Ariel a mano (todavía no hay correo para enviar emails) [decisión de Claude].

### 7.3 Contacto
- **Botón flotante de WhatsApp** en todas las páginas, con mensaje prellenado según la página ("Hola, vi el proyecto X y quiero conversar uno parecido"). Es el canal principal [decisión de Claude: en Chile es donde más se contesta y no requiere formulario].
- El teléfono y el WhatsApp llegan en unos días (número nuevo); el correo info@schobras.cl estará cuando contraten Google Workspace. Por eso todo sale de **Configuración del sitio** y cada elemento solo se muestra si tiene valor. Se puede activar sin volver a publicar el código.

## 8. Pendientes de la clienta (no bloquean el lanzamiento)
- Logo en vector (y retoque final).
- Número de teléfono / WhatsApp.
- Contratar Google Workspace para info@schobras.cl y correos por persona.
- Acceso a la cuenta del dominio (Registrar.eu o el revendedor) para apuntar el DNS.
- Fotos de obras con sus nombres (las carga ella o Ariel desde el panel).
- RUT de la empresa.
- **Confirmar la oferta de arquitectura:** ¿no se cobra nunca si construye con ellos, o se cobra al inicio y se descuenta del presupuesto de obra? Define el titular de la portada.
- **Contacto temporal:** ¿se usa su teléfono actual y oficina@claudiaarquitecta.cl hasta que estén el número nuevo e info@schobras.cl?

**Nombre de marca:** decidido por Ariel el 2026-10-22: **SCHOBRAS.CL** (reemplaza "OBRAS SCH" / "SCH OBRAS").

## 9. Hoja de ruta
- **v1.0 (hoy):** todo lo de este documento.
- **v1.1:** redes sociales (enlaces en pie + Open Graph revisado), cifras de la empresa, dirección si la entregan, y lo que quede pendiente de §8.
- **v2.0:** plataforma con Claude/MCP y generación de planos con IA. Documento aparte.

## 10. Queda a criterio del constructor
- Estructura de apps de Django, nombres de URLs y plantillas.
- Detalle exacto de animaciones, grilla y escala tipográfica, dentro de §4.
- Cómo se reordenan fotos en el panel (arrastrar o flechas).
- Visor de galería.
- Ajuste fino de los textos dentro de §6.
