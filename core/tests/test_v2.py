"""Dirección visual "del plano a la obra" (nació en /v2/; desde el 2026-10-25 es el inicio)."""
import json
import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase, TestCase

from core.tests.test_base import configure

STEP_TITLES = [
    "Visita técnica y entrevista",
    "Presupuesto de arquitectura y especialidades",
    "Estudio y propuesta",
    "Ajustes en conjunto",
    "Proyecto y presupuesto de obra",
    "Construcción con descuento del proyecto",
]


class HomeDesignTests(TestCase):
    """La dirección "del plano a la obra" (ex /v2/) es el inicio desde el 2026-10-25 (aprobada por Claudia)."""

    def get(self, path="/"):
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        return response, response.content.decode()

    def test_home_renders_the_design(self):
        response, _ = self.get()
        self.assertTemplateUsed(response, "core/home.html")
        self.assertTemplateNotUsed(response, "core/home_v2.html")

    def test_home_is_indexable(self):
        _, html = self.get()
        self.assertNotIn('name="robots"', html)

    def test_old_v2_url_redirects_to_home(self):
        response = self.client.get("/v2/")
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response["Location"], "/")

    def test_assets_are_local_and_script_has_nonce(self):
        _, html = self.get()
        self.assertRegex(html, r'<link rel="stylesheet" href="/static/css/v2\.css">')
        self.assertRegex(html, r'<script src="/static/js/v2\.js" defer nonce="[^"]+"></script>')

    def test_keeps_the_texts(self):
        """Nuestra información manda: el contenido es el de textos-v1.md."""
        _, html = self.get()
        self.assertRegex(html, r"<h1[^>]*>\s*Diseñamos y construimos tu proyecto.\s*</h1>")
        self.assertIn(
            "Si construyes con nosotros, el valor del proyecto de arquitectura se descuenta del presupuesto de la obra.",
            html,
        )
        for title in STEP_TITLES:
            self.assertIn(title, html)
        for section in ("Nosotros", "Servicios", "Zona de trabajo"):
            self.assertIn(section, html)
        self.assertEqual(html.count("<h1"), 1)

    def test_process_steps_drive_the_build(self):
        _, html = self.get()
        section = re.search(r'<section[^>]*id="proceso".*?</section>', html, re.S).group(0)
        self.assertIn("data-build", section)
        steps = re.search(r"<ol[^>]*data-build-steps[^>]*>(.*?)</ol>", section, re.S).group(1)
        self.assertEqual(steps.count("<li"), 6)

    def test_hero_3d_is_progressive(self):
        """La portada 3D carga three.js solo bajo demanda; el plano SVG queda de respaldo."""
        _, html = self.get()
        hero = re.search(r'<section class="v2-hero"[^>]*>.*?</section>', html, re.S).group(0)
        self.assertRegex(hero, r'data-hero3d-module="/static/js/v2-hero3d\.min\.js"')
        self.assertRegex(hero, r'<div class="v2-hero__scene" aria-hidden="true" data-scene>')
        self.assertIn('class="v2-plan', hero)
        self.assertIn('<p class="v2-hero__progress">Avance de obra <span data-progress>0</span> %</p>', hero)
        stages = re.search(r"<ol[^>]*data-stages[^>]*>(.*?)</ol>", hero, re.S).group(1)
        self.assertEqual(re.findall(r'data-at="([0-9.]+)"', stages), ["0", "0.05", "0.22", "0.5", "0.78"])
        # Los servicios son textos existentes de textos-v1.md (Servicios), no inventados.
        for text in ("Proyecto de arquitectura a la medida.", "Llave en mano o con el nivel de terminaciones que necesites."):
            self.assertIn(text, stages)
        self.assertNotIn("v2-hero3d.min.js\"></script>", html)

    def test_hero_is_a_house_not_the_process_one(self):
        """Claudia (2026-10-25): la portada es una casa bien terminada, distinta de la del Proceso (12,00 m)."""
        _, html = self.get()
        hero = re.search(r'<section class="v2-hero"[^>]*>.*?</section>', html, re.S).group(0)
        self.assertIn(">17,00</text>", hero)
        self.assertIn(">11,00</text>", hero)
        self.assertNotIn(">24,00</text>", hero)

    def test_poster_is_preloaded_only_when_3d_applies(self):
        _, html = self.get()
        preloads = re.findall(r'<link rel="preload" as="image"[^>]*>', html)
        self.assertEqual(len(preloads), 2)
        for link in preloads:
            self.assertIn("(scripting: enabled) and (prefers-reduced-motion: no-preference) and (min-height: 34em)", link)

    def test_photoreal_render_closes_the_animation_and_says_so(self):
        """Ariel (2026-10-25): al final, una casa que cueste distinguir de una foto. Como la casa no
        existe, se dice: «Imagen referencial» (no se hace pasar por una obra de la empresa)."""
        _, html = self.get()
        scene = re.search(r"<div class=\"v2-hero__scene\".*?</ol>", html, re.S).group(0)
        self.assertIn('<div class="v2-hero__render" data-render></div>', scene)
        self.assertIn('<p class="v2-hero__note" data-render-note>Imagen referencial</p>', scene)

    def test_drawings_are_decorative(self):
        _, html = self.get()
        for svg_class in ("v2-plan", "v2-stage"):
            self.assertRegex(html, rf'<(?:figure|div) class="{svg_class}[^"]*" aria-hidden="true">')

    def test_nav_points_to_home(self):
        _, html = self.get()
        self.assertIn('href="/#nosotros"', html)
        self.assertNotIn("/v2/", html)

    def test_cta_tab_still_deferred(self):
        configure(whatsapp="912345678")
        _, html = self.get()
        self.assertIn("cta-tab--deferred", html)

    def test_old_v2_template_is_gone(self):
        self.assertFalse((Path(settings.BASE_DIR) / "core" / "templates" / "core" / "home_v2.html").exists())


class V2StaticTests(SimpleTestCase):
    def read(self, relative):
        return (Path(settings.BASE_DIR) / "static" / relative).read_text(encoding="utf-8")

    def test_v2_js_under_budget(self):
        self.assertLess(len(self.read("js/v2.js").encode()), 20 * 1024)

    def test_mobile_stage_is_at_most_a_sixth_of_the_screen(self):
        css = self.read("css/v2.css")
        rule = re.search(r"\n\.v2-stage \{([^}]*)\}", css).group(1)
        self.assertIn("height: calc(100svh / 6);", rule)

    def test_build_starts_when_the_drawing_is_fully_in_view(self):
        """El avance arranca cuando el dibujo ya quedó fijo y completo, no cuando la lista asoma."""
        js = self.read("js/v2.js")
        self.assertIn("stage.offsetHeight", js)
        self.assertIn("getComputedStyle(stage).top", js)

    def test_hero3d_bundle_is_local_and_licensed(self):
        bundle = self.read("js/v2-hero3d.min.js")
        self.assertIn("three.js authors", bundle)
        self.assertNotIn("http://", bundle.replace("http://www.w3.org", ""))
        self.assertLess(len(bundle.encode()), 700 * 1024)

    def test_hero3d_loads_only_when_motion_and_webgl_are_available(self):
        js = self.read("js/v2.js")
        self.assertIn("import(", js)
        self.assertIn("webgl", js.lower())

    def test_poster_shows_the_first_frame_while_3d_loads(self):
        """Ariel (2026-10-25): al entrar no debe verse otro plano que después cambia; se ve una
        imagen fija del primer cuadro de la escena, con el mismo encuadre (4:5, cover)."""
        css = self.read("css/v2.css")
        for width in (400, 800, 720, 1440):
            self.assertIn(f'url("../img/portada-plano-{width}.webp")', css)
            self.assertTrue((Path(settings.BASE_DIR) / "static" / "img" / f"portada-plano-{width}.webp").exists())
        self.assertIn("50% 50% / cover no-repeat", css)
        self.assertRegex(css, r"\.v2-hero:not\(\.no-3d\) \.v2-plan__svg \{[^}]*visibility: hidden;")
        source = (Path(settings.BASE_DIR) / "frontend" / "src" / "v2-hero3d.js").read_text()
        self.assertIn("const POSTER_ASPECT = 0.8;", source)

    def test_small_phones_with_large_text_keep_room_for_the_3d(self):
        """Samsung de Claudia (2026-10-25): con la letra del teléfono agrandada, los textos dejaban la
        obra en una franja bajo el título. Modo compacto (en em, sigue la letra) y, si aun así no cabe,
        el plano fijo."""
        css = self.read("css/v2.css")
        self.assertIn("and (max-height: 46em) and (max-width: 63.99em) {", css)
        self.assertIn(".v2-hero:not(.no-3d) .v2-hero__where { display: none; }", css)
        js = self.read("js/v2.js")
        self.assertIn("document.fonts.ready", js)
        self.assertIn("Math.max(140, window.innerHeight * 0.22)", js)

    def test_header_does_not_reserve_the_tab_lane(self):
        """La pestaña de WhatsApp va a media altura: el encabezado usa todo el ancho y no se parte en dos."""
        css = self.read("css/site.css")
        self.assertIn(".site-header { --gutter-end: var(--gutter); }", css)
        self.assertRegex(css, r"@media \(max-width: 21em\) \{\s*html\.js \.menu-toggle__label \{")

    def test_nature_colors_only_inside_the_3d_scene(self):
        """Claudia (2026-10-25): piscina y árboles con sus colores típicos. Es la única excepción a la
        paleta y vive solo en la escena 3D; el CSS sigue solo con tokens."""
        source = (Path(settings.BASE_DIR) / "frontend" / "src" / "v2-hero3d.js").read_text()
        self.assertIn("const NATURE = {", source)
        for key in ("grass:", "water:", "leaves:", "trunk:"):
            self.assertIn(key, source)
        self.assertIn("LineMaterial", source)  # líneas del plano con grosor real
        for name in ("css/site.css", "css/v2.css"):
            self.assertNotIn("#2E9FD0", self.read(name))

    def test_page_frame_lines_are_anthracite(self):
        css = self.read("css/site.css")
        self.assertIn("border-inline: 1px solid var(--axes-color, var(--color-anthracite));", css)

    def test_render_images_exist_and_load_only_with_the_3d(self):
        css = self.read("css/v2.css")
        for width in (400, 800, 720, 1440):
            self.assertIn(f'url("../img/portada-render-{width}.webp")', css)
            self.assertTrue((Path(settings.BASE_DIR) / "static" / "img" / f"portada-render-{width}.webp").exists())
        self.assertIn(".v2-hero.has-render .v2-hero__render {", css)
        source = (Path(settings.BASE_DIR) / "frontend" / "src" / "v2-hero3d.js").read_text()
        # Misma cámara para la escena y el render: posición fija, campo visual recortado como cover.
        self.assertIn("export function cameraPose(", source)
        self.assertIn("export function fovFor(", source)
        self.assertIn("render.style.opacity", source)
        tools = Path(settings.BASE_DIR) / "frontend" / "tools"
        for name in ("export-scene.js", "render-final.py"):
            self.assertTrue((tools / name).exists(), name)

    def test_wide_screens_show_anthracite_sides(self):
        """Claudia (2026-10-25): "la página está muy blanca". Más ancho que la página: costados en
        antracita, el color del pie (Ariel: el cemento no le gustó)."""
        css = self.read("css/site.css")
        html_rule = re.search(r"\nhtml \{([^}]*)\}", css).group(1)
        self.assertIn("background: var(--color-anthracite);", html_rule)
        body_rule = re.search(r"\nbody \{([^}]*)\}", css).group(1)
        for declaration in ("isolation: isolate;", "max-width: var(--max-width);", "margin: 0 auto;", "background: var(--color-white);"):
            self.assertIn(declaration, body_rule)

    def test_wide_screens_frame_the_footer_in_white(self):
        """Ariel (2026-10-25): con los costados en antracita, el pie lleva un borde blanco a los lados y abajo."""
        css = self.read("css/site.css")
        block = re.search(r"@media \(min-width: 90\.0625em\) \{(.*?)\n\}", css, re.S).group(1)
        self.assertIn("border: 4px solid var(--color-white);", block)
        self.assertIn("border-top: 0;", block)

    def test_frontend_tools_are_pinned(self):
        pkg = json.loads((Path(settings.BASE_DIR) / "frontend" / "package.json").read_text())
        self.assertEqual(pkg["devDependencies"], {"esbuild": "0.28.2", "three": "0.186.1"})

    def test_v2_js_respects_reduced_motion(self):
        self.assertIn("prefers-reduced-motion: reduce", self.read("js/v2.js"))

    def test_without_js_the_house_is_finished(self):
        """Sin JS (o con movimiento reducido) el dibujo queda en su estado final: la obra terminada."""
        self.assertRegex(self.read("css/v2.css"), r"\.v2-build\s*\{[^}]*--p:\s*1;")

    def test_v2_css_uses_only_brand_tokens(self):
        css = self.read("css/v2.css")
        self.assertNotRegex(css, r"#[0-9a-fA-F]{3,6}\b")
        self.assertNotRegex(css, r"\brgba?\(|\bhsla?\(")

    def test_v2_transitions_inside_reduced_motion(self):
        stack, outside = [], []
        for number, line in enumerate(self.read("css/v2.css").splitlines(), 1):
            for char in line:
                if char == "{":
                    stack.append("prefers-reduced-motion: no-preference" in line)
                elif char == "}":
                    stack.pop()
            if re.search(r"\b(transition|animation)\s*:", line) and not any(stack):
                outside.append(number)
        self.assertEqual(outside, [])
