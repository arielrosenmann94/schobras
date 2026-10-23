# Guía visual y accesibilidad — SCHOBRAS.CL

Estado: active
Owner: Ariel Rosenmann / desarrollador
Última revisión: 2026-10-22
Versión del documento: 1.0.0
Tipo de cambio más reciente: major
Notas del último cambio: guía inicial de la v1.0
Fuente de verdad: sí
Documentos relacionados: ../2026-10-22-web-v1-diseno.md §4, ../cliente/caracteristicas-pag-web.md, ../../../iterap/docs/06-frontend/FRONTEND_GUIDELINES.md
Objetivo: reglas visuales, de rendimiento y de accesibilidad de la web pública y del panel
Audiencia: desarrollo | agentes

---

## Tokens (en `:root` de `static/css/site.css`)

| Token | Valor | Uso |
|---|---|---|
| `--color-anthracite` | `#2C3539` | Texto principal, estructuras, botón principal, bloques "muro" |
| `--color-bronze` | `#B57949` | Acento: líneas, números de sección grandes, íconos, isotipo |
| `--color-cement` | `#A9ABB6` | Fondos de tarjeta, separadores, bloques secundarios |
| `--color-white` | `#FFFFFF` | Fondo |
| `--color-danger` | `#8A1F1F` | Solo panel (`static/css/panel.css`): errores y botón de borrar |
| `--font-sans` | `"Open Sans", system-ui, sans-serif` | Todo el texto (variable woff2 autoalojada) |

Escala tipográfica con contraste fuerte: display muy grande (`clamp(2.75rem, 8vw, 7rem)`) junto a texto de cuerpo pequeño y aireado (1rem–1.125rem, interlineado 1.6). Espaciado en múltiplos de 8 px.

## Contraste (WCAG 2.2 AA)

| Combinación | Ratio aprox. | Permitido para |
|---|---|---|
| Antracita sobre blanco | ~13:1 | Todo |
| Blanco sobre antracita | ~13:1 | Todo (botón principal) |
| Antracita sobre cemento | ~5,5:1 | Texto normal |
| **Bronce sobre blanco** | **~3,6:1** | **Solo** texto ≥ 24 px (o ≥ 18,66 px negrita), líneas, íconos. **Nunca** texto de cuerpo ni texto blanco sobre bronce |

Verificar el contraste también en `:hover` y `:focus-visible`.

## Dirección visual

- **Lenguaje de plano:** líneas finas tipo cota/grilla, mucho blanco. El fondo lleva solo el marco de dos líneas, medio margen por fuera del contenido: ninguna línea de fondo cruza texto (revisión de Ariel, ronda 1).
- **Pestaña lateral «Cotiza tu proyecto»:** fija al borde derecho, centrada en el alto, texto vertical de abajo hacia arriba; antracita con texto blanco y el canto interior en bronce (solo línea). 44 px de ancho; con ella, el contenido deja libre su carril (`--gutter-end`), así nunca tapa texto. Queda bajo el encabezado y el menú móvil, y bajo el visor de fotos.
- **Muros:** bloques sólidos de antracita/cemento que estructuran la página.
- **Movimiento:** revelado al hacer scroll (bloques que "suben" como muros con `clip-path`/`transform`), líneas que se dibujan, el isotipo armándose con sus verticales (`.rebar`, `stroke-dashoffset`). Una sola vez, rápido (≤ 600 ms), `transform`/`opacity` solamente.
- **Portada sin foto** en la v1.0: composición tipográfica + isotipo.
- Isotipo provisorio en SVG (`static/img/isotipo.svg`) hasta que llegue el logo oficial.

## Accesibilidad (obligatorio)

- Enlace "Saltar al contenido" (`href="#contenido"`) como primer elemento enfocable.
- Landmarks: `<header>`, `<nav aria-label="Principal">`, `<main id="contenido">`, `<footer>`.
- Un solo `<h1>` por página; jerarquía de títulos sin saltos.
- Botones solo-ícono con `aria-label`. La pestaña lateral de WhatsApp lleva texto visible (`Cotiza tu proyecto`) y un `aria-label` que empieza con ese texto (`Cotiza tu proyecto por WhatsApp`, WCAG 2.5.3).
- `:focus-visible` siempre visible (contorno antracita/bronce de 3 px con separación).
- Áreas táctiles ≥ 44 × 44 px (panel: botones ≥ 48 px de alto).
- Menú móvil: `aria-expanded`, `aria-controls`, cierre con Esc, foco devuelto al botón.
- Visor de fotos (`<dialog>`): foco atrapado, Esc cierra, flechas navegan, botones con etiqueta.
- `alt` en toda imagen de proyecto (`alt_text` o el título).
- `prefers-reduced-motion: reduce` → sin animaciones; contenido visible.
- Sin JS, todo el contenido es visible (`.reveal` solo se oculta bajo `html.js`).

## Rendimiento

- Objetivo Lighthouse móvil ≥ 90 (rendimiento y accesibilidad), LCP < 2,5 s.
- JS propio < 20 KB, con `defer` y `nonce`. Sin librerías.
- Fuente: un solo woff2 variable, `preload` + `font-display: swap`.
- Imágenes: `srcset` (400/800/1600) con `sizes`, `width`/`height` siempre, `loading="lazy"` salvo la imagen principal (`fetchpriority="high"`).
- Breakpoints mobile-first: 360, 768, 1024, 1440 px.

## Prohibido

`style="..."` en plantillas, frameworks CSS/JS, CDNs, colores fuera de los tokens, Copperplate como fuente web.

## Cuándo debe actualizarse

Al llegar el logo oficial, al cambiar la paleta o al agregar componentes nuevos.
