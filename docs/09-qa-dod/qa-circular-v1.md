# QA circular entre sesiones — SCHOBRAS.CL v1.0

Estado: active
Owner: Ariel Rosenmann / desarrollador
Última revisión: 2026-10-23
Versión del documento: 1.1.0
Tipo de cambio más reciente: minor
Notas del último cambio: regla del cronómetro de webar (iniciar al empezar, detener al terminar)
Fuente de verdad: sí
Documentos relacionados: definition-of-done.md, ../../.agents/CODING_AGENT_RULES.md, ../superpowers/plans/2026-10-22-web-v1.md
Objetivo: definir cómo la sesión revisora (QA) y la sesión implementadora iteran hasta que la v1.0 esté lista para revisión humana
Audiencia: agentes | qa | desarrollo

---

## Roles

| Sesión | Rol |
|---|---|
| **schobras-89** (implementadora) | Programa el plan, corrige los hallazgos y avisa cuando termina cada vuelta |
| **schobras-c0** (revisora) | Hace QA funcional, de seguridad y de diseño **por código** (lectura, pruebas, `runserver` local con peticiones HTTP reales). No edita código de la aplicación |
| **Ariel** (humano) | Revisión final por pantalla en el servidor local, cuando la revisora diga "listo para el humano" |

## Ciclo

1. La implementadora termina (o termina un bloque) y le manda a la revisora: rama, último commit, qué tasks cerró y cómo levantar el servidor local.
2. La revisora hace QA con la lista de abajo y devuelve un **reporte de vuelta N**: hallazgos numerados `QA-N.k`, cada uno con severidad (🔴 bloqueante, 🟠 importante, 🟡 menor), archivo:línea, cómo reproducirlo y qué se espera.
3. La implementadora corrige **todos** los 🔴 y 🟠 (y los 🟡 que pueda), con una prueba de regresión por cada bug, DoD verde y commits. Después **devuelve** a la revisora: qué hallazgo cerró, con qué commit y con qué prueba.
4. La revisora verifica cada cierre (no confía en el reporte: vuelve a correr) y repite la lista completa sobre lo que cambió.
5. Se repite hasta que una vuelta termina con **0 🔴 y 0 🟠**. Entonces la revisora le dice a la implementadora: **"QA OK — listo para revisión humana"**, y le pasa a Ariel el resumen y los pasos para levantar el servidor local.
6. Los 🟡 que queden se listan para Ariel; él decide si se arreglan antes de mostrar a la clienta.

Reglas del ciclo: la implementadora no hace push ni deploy en ningún momento; la revisora no corrige código de la aplicación (solo puede proponer el cambio); cada mensaje entre sesiones termina pidiendo explícitamente la devolución.

## Cronómetro de trabajo (webar) — regla de Ariel, 2026-10-23

El tiempo de trabajo en schobras se registra en el cronómetro de webar: proyecto **schobras › Web informativa**, tarea **"Desarrollo"**. **Siempre:**

1. **Al empezar a trabajar** (una tarea nueva, una entrega o una vuelta de QA, también cuando la pide Ariel directamente): buscar con `ListAgents` una sesión de **webar** (el nombre cambia: webar-32, webar-93…) y pedirle **iniciar** el cronómetro. Si ya hay un tramo abierto de schobras, no se abre otro. La sesión de webar responde con el número de sesión del cronómetro y la hora.
2. **Al terminar** (el "QA OK — listo para revisión humana", o cuando el trabajo queda terminado o en espera de Ariel): pedirle a la sesión de webar que lo **detenga** (stop). La pausa se usa solo si el trabajo sigue enseguida.
3. **Lo pide una sola sesión, para que no haya avisos dobles:** la revisora (documentación/QA). La implementadora solo verifica con webar que el aviso llegó, y lo pide ella únicamente si la revisora no está.
4. **Si no hay ninguna sesión de webar abierta**, se le avisa a Ariel en el mismo momento. No se deja el trabajo sin registrar en silencio.
5. Ariel puede no estar en pantalla: el inicio y el stop se piden igual, sin esperarlo.

## Lista de QA

### Funcional
- Toda la suite pasa y los gates de `definition-of-done.md` dan la salida esperada.
- Cada task del plan: sus pruebas existen, dicen lo que el plan pide y prueban el comportamiento (no la implementación).
- Review Focus del plan (5 casos) cubiertos con prueba y verificados por HTTP real.
- Recorrido HTTP con `runserver`: `/`, `/proyectos/`, filtro por categoría, detalle, 404, `robots.txt`, `sitemap.xml`, login, panel completo (crear proyecto, subir fotos, portada, ordenar, publicar sin fotos → mensaje, publicar, despublicar, borrar, categorías, configuración solo administrador).
- Con y sin datos de contacto, con y sin proyectos.
- Textos idénticos a `docs/02-producto/textos-v1.md`.

### Seguridad
- Cabeceras: CSP sin `unsafe-inline` y con nonce en cada `<script>`, `X-Frame-Options: DENY`, `nosniff`, Referrer-Policy.
- `check --deploy` con settings de producción (solo W021).
- CSRF en todo POST; ningún cambio de estado por GET.
- Permisos: anónimo → login; editora → 403 en configuración; acceso por UUID ajeno o inexistente → 404, nunca 500.
- django-axes bloquea al sexto intento.
- Subida de archivos: > 15 MB, formatos falsos (texto renombrado `.jpg`), nombres raros → rechazo limpio.
- Sin `|safe` sobre datos de usuario, sin `print`, sin `except Exception` fuera del límite documentado, sin secretos en el repo (`git grep` de claves), `.env` ignorado.
- Ningún campo de dirección; ningún dato personal de visitantes.
- `pip-audit -r requirements.txt` sin vulnerabilidades.

### Diseño (por código)
- Tokens de color de `guia-visual.md` y ningún color fuera de ellos; bronce nunca en texto de cuerpo ni como fondo de texto blanco.
- Sin `style="..."`, sin CDNs, fuente autoalojada con preload.
- Accesibilidad: skip link, landmarks, un `<h1>`, `alt` en imágenes, `aria-label` en botones solo-ícono, `aria-expanded` en menú, `:focus-visible` definido, áreas táctiles ≥ 44 px (panel ≥ 48 px).
- `prefers-reduced-motion` respetado; sin JS el contenido es visible.
- `site.js` < 20 KB; imágenes con `width`/`height`, `srcset`, `loading="lazy"` salvo la principal.
- Mobile-first: media queries en 768 / 1024 / 1440 px.
- Plantillas: sin `{# #}` multilínea, sin tags partidos, sin variables inexistentes (`string_if_invalid` en local).

## Revisión humana (al final)

La revisora entrega a Ariel: commits de la versión, resumen de vueltas de QA, 🟡 pendientes y los comandos exactos para revisar por pantalla:

```bash
cd /home/ars/Escritorio/ariel_it/schobras
./env_schobras/bin/python manage.py migrate
./env_schobras/bin/python manage.py createsuperuser   # si no existe
./env_schobras/bin/python manage.py runserver
# Abrir http://localhost:8000/ y http://localhost:8000/panel/
```
