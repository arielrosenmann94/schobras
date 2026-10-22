# Instructivo estricto para IA codificadora — `schobras`

Estado: active
Owner: Ariel Rosenmann / desarrollador
Última revisión: 2026-10-22
Versión del documento: 1.0.0
Tipo de cambio más reciente: major
Notas del último cambio: versión inicial para la v1.0
Fuente de verdad: sí
Documentos relacionados: ../CLAUDE.md, ../docs/README.md, ../docs/2026-10-22-web-v1-diseno.md
Objetivo: reglas que todo agente debe cumplir al tocar este repositorio
Audiencia: agentes | desarrollo

---

## 1. Regla principal

Implementar exactamente lo que dicen el diseño (`docs/2026-10-22-web-v1-diseno.md`) y el plan (`docs/superpowers/plans/2026-10-22-web-v1.md`). Si algo no está definido y la decisión cambia lo que ve la clienta o un dato, **detenerse y preguntar a Ariel**. Si es una decisión menor de implementación, tomarla y dejarla anotada en el reporte de cierre.

## 2. Lectura obligatoria antes de codificar

1. `CLAUDE.md`
2. Este documento
3. `docs/2026-10-22-web-v1-diseno.md`
4. La task del plan que se va a implementar (y su bloque **Interfaces**)
5. Según la task: `docs/03-dominio/modelo-de-datos.md`, `docs/06-frontend/guia-visual.md`, `docs/07-appsec/seguridad.md`, `docs/02-producto/textos-v1.md`

## 3. Qué se puede editar

| Categoría | Archivos | Regla |
|---|---|---|
| Libre (dentro de la task en curso) | `accounts/`, `core/`, `projects/`, `panel/`, `templates/`, `static/` | Con prueba primero (TDD) y DoD verde |
| Requiere plan previo | Modelos ya migrados y commiteados, `config/settings/*`, `config/urls.py` | Solo si la task lo indica |
| Requiere aprobación humana explícita | `requirements.txt` (dependencia nueva), `.claude/settings.json`, `Procfile`, `.python-version`, cualquier cosa de Heroku/DNS | Preguntar antes |
| Prohibido | `.env*`, `características pág web.docx`, `docs/cliente/`, `respuestas-cliente-*.md` | No tocar |

Dependencias ya aprobadas por Ariel (2026-10-22): `uuid6`, `django-axes`, `cloudinary`, `django-cloudinary-storage`, `pip-audit` (herramienta, fuera de requirements).

## 4. Reglas técnicas no negociables

1. **Idioma:** código en inglés (modelos, campos, funciones, nombres de URL, nombres de apps). Interfaz, mensajes y rutas públicas en español.
2. **Modelos:** heredan `core.models.BaseModel` (UUID v7, `created_at`, `updated_at`); `__str__` y `Meta` (`ordering`, `verbose_name`, `verbose_name_plural`) siempre.
3. **Escrituras de negocio solo en servicios** (`projects/services.py`). Vistas, admin y (en v2.0) API llaman al servicio; nunca duplican la regla.
4. **Forms/ModelForms** con `fields` explícito, nunca `__all__`. Patrón PRG. `{% csrf_token %}` en todo formulario POST.
5. **Cambios de estado por POST**, nunca por GET (publicar, borrar, mover foto, etc.).
6. **CSP nativa** de Django 6: todo `<script>` lleva `nonce="{{ csp_nonce }}"`; nada inline sin nonce; sin `style="..."`.
7. **Sin** `print()`, `except Exception` (salvo límite HTTP documentado, con log), `str(exc)` en respuestas, `|safe` sobre datos de usuario.
8. **Sin frameworks de frontend ni CDN**: CSS y JS propios, fuente autoalojada.
9. **Accesibilidad WCAG 2.2 AA** (ver `docs/06-frontend/guia-visual.md`).
10. **Pruebas:** `python manage.py test` (no pytest). Cada bug arreglado lleva prueba de regresión.
11. **Plantillas:** sin `{# #}` multilínea; sin tags partidos en varias líneas (`{% if\n ... %}`); `string_if_invalid` activo en local para detectar variables faltantes.
12. **Fotos:** nunca un campo de dirección; validar formato (JPEG/PNG/WebP) y tamaño (≤ 15 MB) con mensaje en español.

## 5. Git

- Al empezar: `git status`. No pisar cambios ajenos.
- Conventional Commits: `feat|fix|docs|chore|refactor|test(alcance): descripción` en imperativo, en español.
- Commits atómicos, < 20 archivos; primero lo estructural, después lo nuevo.
- **Nunca `git push`, nunca `git push heroku`, nunca deploy.** Ariel lo hace con aprobación explícita cada vez.
- Nunca `git reset --hard`, `git push --force`, `rm -rf` sobre el repo.

## 6. Prohibiciones absolutas

- Imprimir secretos de producción (ver `CLAUDE.md`).
- Leer o editar `.env*`.
- Instalar dependencias no aprobadas.
- Publicar direcciones de clientes de la constructora.
- Prometer en textos públicos algo que el diseño no dice (años de la empresa, cifras, garantías).
- Mencionar en textos para la clienta información personal que Ariel no autorizó.

## 7. Verificación y cierre

Antes de cada commit, el **Definition of Done** (`docs/09-qa-dod/definition-of-done.md`) completo en verde.

Reporte de cierre de cada task: qué se leyó, qué se cambió, qué se verificó (comandos y resultado real), qué commits se crearon, y qué decisiones menores se tomaron.

## 8. Cumplimiento Chile

- Ley 19.628 / Ley 21.719 (datos personales): la v1.0 no recolecta datos de visitantes (sin formulario, sin analítica, sin cookies propias salvo sesión del panel). Si se agrega un formulario o analítica (v1.1+), primero política de privacidad.
- Fotos de obras: solo con autorización del dueño de la obra (aviso visible en el panel).
