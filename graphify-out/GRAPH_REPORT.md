# Graph Report - /home/ars/Escritorio/ariel_it/schobras  (2026-10-22)

## Corpus Check
- Corpus is ~8,810 words - fits in a single context window. You may not need a graph.

## Summary
- 173 nodes · 248 edges · 42 communities (33 shown, 9 thin omitted)
- Extraction: 69% EXTRACTED · 31% INFERRED · 1% AMBIGUOUS · INFERRED: 76 edges (avg confidence: 0.91)
- Token cost: 129,065 input · 0 output

## Community Hubs (Navigation)
- Marca, contenido y oferta
- Contacto, WhatsApp y reglas del plan
- Personas, modelos y backoffice
- Decisiones y pendientes v1
- Stack y dependencias
- Restricciones y SEO
- Settings Django
- Isotipo de marca
- Usuario propio (accounts)
- App accounts
- App core
- manage.py
- App panel
- App proyectos
- Archivo vacío: migrations/0001_initial.py
- Archivo vacío: config/asgi.py
- Archivo vacío: config/urls.py
- Archivo vacío: config/wsgi.py

## God Nodes (most connected - your core abstractions)
1. `Diseño de la web informativa SCHOBRAS.CL v1.0` - 28 edges
2. `Plan de implementación SCHOBRAS.CL v1.0` - 16 edges
3. `Respuestas del cliente 2026-10-22 (preguntas 1-16)` - 14 edges
4. `SCHOBRAS.CL README` - 11 edges
5. `Task 1: Modelos de proyectos y admin de respaldo` - 11 edges
6. `Características página web (documento de la clienta)` - 10 edges
7. `Decisiones web informativa SCH Obras v1` - 8 edges
8. `Página de inicio de una sola página con anclas` - 8 edges
9. `Task 3: Base visual (plantilla, CSS, fuentes, JS)` - 8 edges
10. `Stack alineado con iterap y admindf` - 7 edges

## Surprising Connections (you probably didn't know these)
- `Modelo Categoría de proyecto` --implements--> `Proyectos y categorías administrables`  [INFERRED]
  docs/2026-10-22-web-v1-diseno.md → decisiones-v1.md
- `Alcance: v1.0 informativa, v2.0 Claude/MCP con planos dictados` --semantically_similar_to--> `v2.0: plataforma Claude/MCP y generación de planos con IA`  [INFERRED] [semantically similar]
  respuestas-cliente-2026-10-22.md → docs/2026-10-22-web-v1-diseno.md
- `Configuración del sitio (registro único: WhatsApp, teléfono, correo)` --rationale_for--> `Contacto: teléfono/WhatsApp nuevo en días, info@ + correos por persona`  [INFERRED]
  docs/2026-10-22-web-v1-diseno.md → respuestas-cliente-2026-10-22.md
- `App accounts (User propio y roles)` --implements--> `Roles Editora y Administrador`  [INFERRED]
  README.md → docs/2026-10-22-web-v1-diseno.md
- `Arquitectura: Django SSR con apps core, proyectos, accounts, panel` --references--> `App core (páginas públicas, 404, sitemap, robots)`  [INFERRED]
  docs/superpowers/plans/2026-10-22-web-v1.md → README.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Modelo de datos del catálogo de proyectos** — docs_2026_10_22_web_v1_diseno_modelo_categoria, docs_2026_10_22_web_v1_diseno_modelo_proyecto, docs_2026_10_22_web_v1_diseno_modelo_foto_proyecto, docs_2026_10_22_web_v1_diseno_configuracion_sitio, docs_superpowers_plans_2026_10_22_web_v1_task1_modelos_proyectos, docs_superpowers_plans_2026_10_22_web_v1_slug_unico, docs_superpowers_plans_2026_10_22_web_v1_proyecto_publicados [INFERRED 0.85]
- **Contacto condicional según Configuración del sitio** — docs_2026_10_22_web_v1_diseno_configuracion_sitio, docs_2026_10_22_web_v1_diseno_whatsapp_flotante, docs_superpowers_plans_2026_10_22_web_v1_normalizar_numero, docs_superpowers_plans_2026_10_22_web_v1_context_processor_sitio, docs_superpowers_plans_2026_10_22_web_v1_task2_configuracion_whatsapp, docs_superpowers_plans_2026_10_22_web_v1_task11_panel_configuracion, respuestas_cliente_2026_10_22_contacto_numero_nuevo [INFERRED 0.85]
- **Backoffice a medida para la editora** — docs_2026_10_22_web_v1_diseno_backoffice_panel, docs_2026_10_22_web_v1_diseno_roles_editora_administrador, docs_2026_10_22_web_v1_diseno_protecciones_editora, docs_superpowers_plans_2026_10_22_web_v1_panelmixin_administradormixin, docs_superpowers_plans_2026_10_22_web_v1_task8_roles_acceso_panel, docs_superpowers_plans_2026_10_22_web_v1_task9_panel_proyectos_categorias, docs_superpowers_plans_2026_10_22_web_v1_task10_panel_fotos, docs_superpowers_plans_2026_10_22_web_v1_task11_panel_configuracion, decisiones_v1_backoffice_propio [INFERRED 0.85]
- **Building-under-construction motif** — static_img_isotipo_building_silhouette, static_img_isotipo_rebar_scaffold_lines, static_img_isotipo_ground_line [INFERRED 0.85]

## Communities (42 total, 9 thin omitted)

### Community 0 - "Marca, contenido y oferta"
Cohesion: 0.10
Nodes (26): Dominio schobras.cl (Registrar.eu, HTTPS, www redirige), Identidad de marca: antracita, bronce, cemento, blanco + Open Sans, Logo Copperplate como imagen, isotipo provisorio, Nombre de marca SCHOBRAS.CL (reemplaza OBRAS SCH / SCH OBRAS), Página de inicio de una sola página con anclas, Pilar: arquitectura y trámites municipales sin costo si construyes con nosotros, Proceso de 6 pasos, Público principal: personas y familias residenciales (+18 more)

### Community 1 - "Contacto, WhatsApp y reglas del plan"
Cohesion: 0.22
Nodes (21): Configuración del sitio (registro único: WhatsApp, teléfono, correo), Protecciones para la editora (no borrar categorías con proyectos, confirmaciones, aviso de permisos de fotos), Botón flotante de WhatsApp con mensaje prellenado, Context processor core.context_processors.sitio (sitio, whatsapp_href, hay_contacto, hay_proyectos), normalizar_numero() / whatsapp_url() para formatos chilenos, PanelMixin y AdministradorMixin, Plan de implementación SCHOBRAS.CL v1.0, Proyecto.objects.publicados() (excluye borradores y proyectos sin fotos) (+13 more)

### Community 2 - "Personas, modelos y backoffice"
Cohesion: 0.15
Nodes (20): Ariel Rosenmann (autor, rol administrador), Backoffice /panel/ a medida, móvil, en español, Claudia Schonffeldt (dueña, arquitecta, rol editora), Cloudinary para fotos de proyectos, Constructora Schonffeldt SpA (marca SCHOBRAS.CL), Cuentas Heroku y Cloudinary a nombre de Claudia, Dirección visual: contraste de escala, lenguaje de plano, muros, portada sin foto, Diseño de la web informativa SCHOBRAS.CL v1.0 (+12 more)

### Community 3 - "Decisiones y pendientes v1"
Cohesion: 0.15
Nodes (17): Backoffice propio (no admin de Django), Correo vía Google Workspace (info@schobras.cl), Diseño y UX los decide Ariel, no la clienta, Decisiones web informativa SCH Obras v1, Proyectos y categorías administrables, Redes sociales diferidas a v1.1, Pendientes de la clienta (logo, teléfono, Workspace, DNS, fotos, RUT, confirmar oferta), v1.1: redes, cifras, dirección y pendientes (+9 more)

### Community 4 - "Stack y dependencias"
Cohesion: 0.22
Nodes (12): Stack Django definido por Ariel, Stack alineado con iterap y admindf, v2.0: plataforma Claude/MCP y generación de planos con IA, Stack Python 3.12 / Django 6.0 / PostgreSQL / Heroku, dj-database-url==3.1.2, Django==6.0.6, gunicorn==23.0.0, pillow==13.0.0 (+4 more)

### Community 5 - "Restricciones y SEO"
Cohesion: 0.24
Nodes (10): Anti-objetivos (plantilla genérica, lentitud, publicar direcciones, sobreprometer), "Más de 25 años" atribuido a los profesionales, No-objetivos v1.0 (formulario, redes, cifras, misión, dirección, etc.), SEO: sitemap, robots, Open Graph, JSON-LD GeneralContractor sin dirección, Proyecto sin campo de dirección (a propósito), Quiénes somos, Global Constraints del plan, Open Sans autoalojada (woff2 variable, subconjunto latino) (+2 more)

### Community 6 - "Settings Django"
Cohesion: 0.29
Nodes (3): config/settings/base.py ─────────────────────── Configuración base compartida en, config/settings/local.py ──────────────────────── Settings para desarrollo local, config/settings/production.py ───────────────────────────── Settings de producci

### Community 7 - "Isotipo de marca"
Cohesion: 0.33
Nodes (7): Architecture + Construction Duality, Stepped Building Silhouette, Ground Baseline, SCHOBRAS Isotipo (brand mark), Possible Letterform in Negative Space, Monochrome Charcoal Palette, Rebar / Scaffolding Vertical Lines

### Community 8 - "Usuario propio (accounts)"
Cohesion: 0.50
Nodes (3): AbstractUser, Usuario de SCHOBRAS.CL.      Existe desde la primera migración para poder agrega, User

## Ambiguous Edges - Review These
- `Dirección visual: contraste de escala, lenguaje de plano, muros, portada sin foto` → `Referencia: jfconstructora.com`  [AMBIGUOUS]
  respuestas-cliente-2026-10-22.md · relation: conceptually_related_to
- `Stepped Building Silhouette` → `Possible Letterform in Negative Space`  [AMBIGUOUS]
  static/img/isotipo.png · relation: conceptually_related_to

## Knowledge Gaps
- **7 isolated node(s):** `Migration`, `Settings config.settings.local / production`, `Objetivos v1.0 (claridad, estética arquitectónica, rapidez, panel propio)`, `Nombre de marca SCHOBRAS.CL (reemplaza OBRAS SCH / SCH OBRAS)`, `Ground Baseline` (+2 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Dirección visual: contraste de escala, lenguaje de plano, muros, portada sin foto` and `Referencia: jfconstructora.com`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Stepped Building Silhouette` and `Possible Letterform in Negative Space`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `Diseño de la web informativa SCHOBRAS.CL v1.0` connect `Personas, modelos y backoffice` to `Marca, contenido y oferta`, `Contacto, WhatsApp y reglas del plan`, `Decisiones y pendientes v1`, `Stack y dependencias`, `Restricciones y SEO`?**
  _High betweenness centrality (0.191) - this node is a cross-community bridge._
- **Why does `Plan de implementación SCHOBRAS.CL v1.0` connect `Contacto, WhatsApp y reglas del plan` to `Marca, contenido y oferta`, `Personas, modelos y backoffice`, `Decisiones y pendientes v1`, `Restricciones y SEO`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Why does `Respuestas del cliente 2026-10-22 (preguntas 1-16)` connect `Marca, contenido y oferta` to `Personas, modelos y backoffice`, `Decisiones y pendientes v1`, `Stack y dependencias`, `Restricciones y SEO`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `Task 1: Modelos de proyectos y admin de respaldo` (e.g. with `Modelo Categoría de proyecto` and `Modelo Foto de proyecto (Cloudinary, portada, alt)`) actually correct?**
  _`Task 1: Modelos de proyectos y admin de respaldo` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Migration`, `Settings config.settings.local / production`, `Objetivos v1.0 (claridad, estética arquitectónica, rapidez, panel propio)` to the rest of the system?**
  _7 weakly-connected nodes found - possible documentation gaps or missing edges._