# Definition of Done — SCHOBRAS.CL

Estado: active
Owner: Ariel Rosenmann / desarrollador
Última revisión: 2026-10-22
Versión del documento: 1.0.0
Tipo de cambio más reciente: major
Notas del último cambio: DoD inicial basada en webar e iterap
Fuente de verdad: sí
Documentos relacionados: ../../../webar/docs/quality/DEFINITION_OF_DONE.md, ../../.agents/CODING_AGENT_RULES.md
Objetivo: definir cuándo una task, un commit y la versión están terminados
Audiencia: desarrollo | agentes | qa

---

## Una task está terminada cuando

1. Las pruebas de la task se escribieron **antes** del código y fallaron por la razón esperada.
2. Toda la suite pasa.
3. Los gates de abajo están en verde (salida real, no supuesta).
4. Se commiteó con Conventional Commits.
5. El reporte de cierre dice qué se leyó, qué se cambió, qué se verificó y qué decisiones menores se tomaron.

## Gates (copiar y correr)

```bash
PY=./env_schobras/bin/python
$PY manage.py test
$PY manage.py check
$PY manage.py makemigrations --check --dry-run
# Sin resultados esperados:
grep -rnE 'style="|print\(|except Exception' --include=*.py --include=*.html accounts core projects panel templates
grep -rn '{#' --include=*.html accounts core projects panel templates | grep -v '#}'
grep -rnE '\{%[^%]*$' --include=*.html accounts core projects panel templates
git diff --check
```

Si `except Exception` aparece, solo se acepta en un límite HTTP documentado y con log.

## Gates de producción (antes de entregar a Ariel para desplegar)

```bash
DJANGO_SETTINGS_MODULE=config.settings.production \
DATABASE_URL=postgres://u:p@h:5432/x SECRET_KEY="$(openssl rand -base64 48)" \
CLOUDINARY_URL=cloudinary://k:s@demo \
$PY manage.py check --deploy          # solo W021 (preload, intencional)
# mismas variables:
$PY manage.py collectstatic --noinput --dry-run
pip-audit -r requirements.txt         # sin vulnerabilidades
wc -c static/js/site.js               # < 20000
```

## La v1.0 está terminada cuando

- [ ] Tasks 0–11 del plan commiteadas con DoD verde.
- [ ] Revisión visual en 360 px y 1440 px (inicio, lista, detalle, panel).
- [ ] Navegación completa solo con teclado (menú, visor, panel).
- [ ] Desplegada por Ariel; fase `release` OK; `showmigrations` sin pendientes.
- [ ] Lighthouse móvil en producción ≥ 90 en rendimiento y accesibilidad.
- [ ] Al menos un canal de contacto configurado.
- [ ] Usuario de Claudia creado (rol editora) y probado.
- [ ] `graphify update .` corrido.
