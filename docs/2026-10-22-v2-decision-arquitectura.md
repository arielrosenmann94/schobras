# SCHOBRAS.CL v2.0 — Decisión de arquitectura

**Estado:** decisión tomada (Claude, por encargo de Ariel, 2026-10-22). Antes de construir, se hace la spec completa con brainstorming, después de entregar la v1.
**Insumos:**
- Recomendaciones que trajo Ariel ("SCHOBRAS 2.0: Claude Code + Django + MCP + generación local de planos").
- Skill `conector-mcp-admindf` y `iterap/mcp_server_iterap.py` + `iterap/docs/05-api/CLAUDE_MCP_CONECTOR.md`.
- Verificación de fuentes primarias hecha el 2026-10-22 (§6).

## 1. Qué se quiere

Que Claudia (arquitecta, dueña) maneje SCHOBRAS conversando con Claude, **principalmente por voz**. Debe poder:
- Consultar y actualizar todo lo que existe en las versiones 1.x (proyectos, categorías, fotos, contenidos y lo que se sume).
- Diseñar proyectos dictando sus características. La IA genera borradores que se transforman en planos listos para entregar, **siempre revisados, aprobados y firmados por ella**.

Ariel pidió que todo pase por el backend de SCHOBRAS y que el entorno agéntico siga el modelo de admindf.

## 2. Decisiones

### D1. Django es el sistema de registro y no ejecuta IA
Se adopta la recomendación. La web en Heroku guarda y administra la información. No llama a la API de Anthropic, no genera planos y no aloja un MCP remoto. Claude corre en el computador de Claudia con **su suscripción Pro/Max**, sin `ANTHROPIC_API_KEY` en el entorno (si esa variable existe, el cobro pasa a tarifa de API).

### D2. Dos servidores MCP locales (stdio), los dos hechos por nosotros
| MCP | Qué hace | Base |
|---|---|---|
| **schobras** | Cliente HTTP puro (`httpx`) contra una API de Django con token propio | Patrón del conector de admindf |
| **planos** | Modelo de planta propio en JSON, validación geométrica determinista, exporta DXF y genera una vista previa PNG para que Claude "vea" el resultado | `ezdxf` (MIT) |

**No se adopta IfcMCP como herramienta principal.** Existe y es oficial de IfcOpenShell, pero:
- El paquete real se llama `ifcopenshell-mcp`; `ifcmcp` da 404 en PyPI.
- Tiene 7 meses y dos versiones.
- Expone la API IFC genérica (`ifc_edit` ejecuta cualquier llamada de la API), que es demasiado amplia para que la use una arquitecta conversando.

Se puede usar como herramienta de desarrollo o de inspección, no como la interfaz de Claudia.

### D3. Nivel de automatización: primero 2D (nivel A), con un modelo listo para BIM
La recomendación proponía empezar directo con BIM 3D (nivel B). **Se decide empezar por 2D**, con un modelo interno pensado para pasar a IFC después:
- Lo que Claudia entrega y edita hoy son plantas. Un DXF lo abre cualquier programa CAD, sin depender de que el BIM funcione.
- Claude es impreciso con la geometría: cierres de muros, vanos fuera del muro, cotas. El riesgo se controla con un modelo simple más validación determinista en el servidor, no con una API BIM completa.
- El mismo JSON (muros como segmentos con espesor, vanos, recintos con nombre, niveles) se exporta a IFC en la fase 2 con `ifcopenshell.api` (`create_2pt_wall`, aberturas y losas). Pasar a BIM no obliga a rehacer nada.
- El nivel C (láminas, cortes, elevaciones y cuadros de superficie) viene después, sujeto a revisión profesional.

### D4. La interfaz de Claudia es la app de escritorio de Claude, no la terminal
- Claude Code (terminal o pestaña Code) está pensado para desarrolladores. Para Claudia: **Claude Desktop (chat) con los dos MCP empaquetados como extensiones `.mcpb`**, que se instalan con un clic.
- **Voz:** el dictado de la app de escritorio, o el del sistema operativo como respaldo universal. `/voice` de Claude Code soporta español, pero vive en la terminal.
- Ariel usa Claude Code para desarrollar y operar, como en admindf.

### D5. El MCP schobras sigue las reglas del conector de admindf
- **Autenticación:** Bearer con un token propio (`SCHOBRAS_MCP_TOKEN`), distinto de cualquier otro, comparado con `hmac.compare_digest`. **Fail-closed:** sin token configurado, se niega todo.
- **Lecturas** envuelven selectores probados. **Escrituras** envuelven `projects/services.py` (la única puerta, que ya existe desde la v1). Nunca ORM crudo en la vista.
- **Dry-run por defecto** y `apply` aceptado solo si `body.get("apply") is True`. Números siempre `int`, nunca `float`.
- **Serializadores explícitos** por modelo, nunca `model_to_dict` genérico.
- **Alcance inicial:** lectura de todo, escritura de crear, editar, publicar y despublicar. **Los borrados quedan fuera** al principio: minimización, igual que el remoto de admindf.
- **Pruebas:** la verificación final es por **HTTP real**, no llamando funciones dentro del proceso. `/security-review` antes de cada push que agregue escrituras.
- **Secretos:** los genera y configura Ariel en su terminal; el agente nunca los ve.

### D6. SDK de MCP: rama 1.x, como iterap
El paquete `mcp` 2.x renombró `FastMCP` a `MCPServer` y `from mcp.server.fastmcp import FastMCP` falla. iterap usa `mcp==1.26.0`. Se fija `mcp>=1.26,<2` con FastMCP para mantener la consistencia entre repos, y la migración a 2.x se evalúa aparte.

### D7. Archivos de planos
- Los originales viven en el computador de Claudia, en una carpeta de proyectos con versiones: cada cambio guarda una versión nueva y no pisa la anterior.
- A Django se suben los metadatos, la vista previa y los entregables (DXF y PDF), en un **bucket S3 privado** con URLs firmadas, el patrón de adjuntos de iterap. **No van a Cloudinary público**: son planos de clientes.
- Esto suma un costo de almacenamiento que hay que comunicar a Claudia.

### D8. Entorno agéntico al estilo admindf
La v1 ya trae CLAUDE.md, AGENTS.md y `.claude/settings.json` (bloqueo de secretos de Heroku y de `git push`, hooks de graphify). La v2 suma:
- El conector MCP.
- Las tools del MCP en `allow` del proyecto.
- `docs/claude-code/` (configuración del entorno, flujo agéntico, seguridad), copiando la estructura de admindf.
- Skills propias del proyecto cuando aparezcan patrones que valga la pena repetir.

## 3. Orden de trabajo
1. **Spike del motor de planos** (desechable, fuera de la web). A partir de una descripción dictada debe:
   - generar la planta en JSON,
   - validarla (muros cerrados, vanos dentro de los muros, superficies por recinto),
   - exportar DXF más una vista previa PNG,
   - aplicar una modificación conservando la versión anterior.

   Se prueba con una casa de un piso. Criterio de éxito: Claudia abre el DXF en su programa y lo considera una base útil.
2. Si el spike funciona: spec y plan del **MCP planos**, empaquetado `.mcpb`.
3. **API de Django + MCP schobras**, sobre los servicios de la v1.
4. Exportación IFC (nivel B) y después la documentación (nivel C).

## 4. Riesgos
- **Límites de uso de Pro/Max:** sesiones largas de diseño pueden toparlos. Hay que medirlo en el spike.
- **Precisión geométrica:** se mitiga con validación determinista y vista previa; nunca se entrega sin revisión de la arquitecta.
- **Instalación en su computador:** Python o uv más las extensiones. Se mitiga con `.mcpb` e instalación acompañada.
- **Dependencias jóvenes o con cambios recientes:** `mcp` 2.x, ifcopenshell-mcp. Se mitiga fijando versiones.

## 5. Qué cambia en la v1 por esta decisión
Nada nuevo para el lunes. Ya está en el plan de la v1: PK UUID v7 (IDs estables para la API), `projects/services.py` como única puerta de escritura y modelos en inglés con `created_at`/`updated_at`.

## 6. Verificación de la recomendación original (fuentes primarias, 2026-10-22)
- IfcMCP: **parcial**. Es oficial (LGPLv3+), pero el paquete es `ifcopenshell-mcp`; `pip install 'ifcmcp[mcp]'` falla. — github.com/IfcOpenShell/IfcOpenShell/tree/v0.8.0/src/ifcmcp, pypi.org/project/ifcopenshell-mcp
- IfcOpenShell 0.9.0.post1: **cierto**. Wheels para Python 3.12 en Linux, macOS y Windows. — pypi.org/project/ifcopenshell
- ezdxf 1.4.5 (MIT): **cierto**. — pypi.org/project/ezdxf
- Claude Code con Pro/Max sin API key y MCP stdio: **cierto**. — support.claude.com/en/articles/11145838, code.claude.com/docs/en/mcp
- Extensiones `.mcpb` para Claude Desktop: anthropic.com/engineering/desktop-extensions
- Dictado: code.claude.com/docs/en/voice-dictation
- SDK `mcp` 2.3.0 con FastMCP renombrado: pypi.org/project/mcp, py.sdk.modelcontextprotocol.io/migration
- Referencias de diseño: ArchLang (DSL de plantas a SVG, DXF y PDF, con MCP, MIT) y FreeCAD MCP (neka-nat, MIT).
