# Modelo de datos — SCHOBRAS.CL

Estado: active
Owner: Ariel Rosenmann / desarrollador
Última revisión: 2026-10-22
Versión del documento: 1.0.0
Tipo de cambio más reciente: major
Notas del último cambio: modelo inicial de la v1.0
Fuente de verdad: sí
Documentos relacionados: ../2026-10-22-web-v1-diseno.md §7, ../04-arquitectura/adr/ADR-0001-uuid-v7.md, ../04-arquitectura/adr/ADR-0004-servicios-unica-puerta.md
Objetivo: definir modelos, campos, reglas e invariantes de datos de la v1.0
Audiencia: desarrollo | agentes

---

## Alcance

Apps `core`, `accounts` y `projects`. El panel no tiene modelos propios.

## Base común

`core.models.BaseModel` (abstracto):

| Campo | Tipo | Nota |
|---|---|---|
| `id` | `UUIDField(primary_key=True, default=uuid6.uuid7, editable=False)` | UUID v7 (ordenable por tiempo) |
| `created_at` | `DateTimeField(auto_now_add=True)` | |
| `updated_at` | `DateTimeField(auto_now=True)` | |

## accounts.User

`AbstractUser` + `id` UUID v7.

| Campo | Tipo | Valores |
|---|---|---|
| `role` | `CharField(choices)` | `editor` "Editora" (default), `admin` "Administrador" |

`is_admin_role` → `True` si `is_superuser` o `role == "admin"`.

Usuarios iniciales: Claudia Schonffeldt (oficina@claudiaarquitecta.cl, `editor`), Ariel Rosenmann (hola@arielrosenmann.com, superusuario).

## core.SiteSettings (registro único)

| Campo | Tipo | Nota |
|---|---|---|
| `whatsapp` | `CharField(20, blank)` | Se normaliza a `569XXXXXXXX`; inválido = botón oculto |
| `phone` | `CharField(20, blank)` | Texto visible tal cual |
| `email` | `EmailField(blank)` | |
| `whatsapp_message` | `CharField(200)` | Default "Hola, quiero conversar sobre un proyecto." |

`SiteSettings.load()` devuelve o crea el único registro. Solo lo edita el rol administrador.

## projects.Category

| Campo | Tipo | Nota |
|---|---|---|
| `name` | `CharField(80, unique)` | |
| `slug` | `SlugField(unique, editable=False)` | Se genera una vez |
| `order` | `PositiveIntegerField(default=0)` | |
| `is_active` | `BooleanField(default=True)` | Inactiva = no aparece en filtros; sus proyectos siguen visibles |

Carga inicial: Residencial (1), Comercial (2), Industrial (3).

## projects.Project

| Campo | Tipo | Nota |
|---|---|---|
| `title` | `CharField(150)` | |
| `slug` | `SlugField(170, unique, editable=False)` | Se fija al crear; **no cambia al editar el título** (enlaces estables) |
| `category` | `FK(Category, on_delete=PROTECT, related_name="projects")` | No se puede borrar una categoría con proyectos |
| `intervention_type` | choices | `new_build` Obra nueva · `extension` Ampliación · `remodel` Remodelación |
| `commune` | `CharField(80)` | Solo comuna. **No existe campo de dirección.** |
| `region` | choices | `metropolitana` Región Metropolitana · `valparaiso` Región de Valparaíso · `ohiggins` Región de O'Higgins |
| `construction_systems` | `JSONField(list)` | Claves de: `masonry` Albañilería · `reinforced_concrete` Hormigón armado · `timber` Madera · `volcometal` Volcometal · `sip_panels` Paneles SIP · `steel` Estructuras metálicas |
| `area_m2` | `PositiveIntegerField(null)` | Opcional |
| `year` | `PositiveSmallIntegerField(null)` | Opcional |
| `description` | `TextField(blank)` | |
| `status` | choices | `draft` Borrador (default) · `published` Publicado |
| `is_featured` | `BooleanField` | Aparece en la portada (máx. 6) |
| `order` | `PositiveIntegerField` | Orden manual |

## projects.ProjectPhoto

| Campo | Tipo | Nota |
|---|---|---|
| `project` | `FK(Project, CASCADE, related_name="photos")` | |
| `image` | `ImageField(upload_to="proyectos/%Y/%m/")` | S3 en producción (ADR-0006) |
| `order` | `PositiveIntegerField` | |
| `is_cover` | `BooleanField` | Máximo una por proyecto |
| `alt_text` | `CharField(200, blank)` | Vacío → se usa el título |
| `kind` | choices (blank) | `finished` Obra terminada · `in_progress` En proceso · `render` Render |

## Invariantes

1. **Un proyecto es público solo si** `status == "published"` **y** tiene ≥ 1 foto (`Project.objects.published()`). Un proyecto publicado al que le borran todas las fotos desaparece de la web sin error.
2. Publicar sin fotos lanza `PublishError("Agrega al menos una foto antes de publicar.")`.
3. Una sola portada por proyecto; si no hay marcada, la portada es la foto de menor `order`.
4. Slugs únicos (`casa-chicureo`, `casa-chicureo-2`…) y estables.
5. Ningún modelo guarda direcciones, RUT de clientes ni datos de visitantes.

## Cómo validar que sigue vigente

`python manage.py test projects core accounts` y comparar los modelos con esta tabla.

## Cuándo debe actualizarse

Con cada migración que agregue, quite o cambie un campo o una regla.
