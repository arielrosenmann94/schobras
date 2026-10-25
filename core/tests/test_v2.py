"""Versión de diseño /v2/ ("del plano a la obra"): mismo contenido, otra dirección visual, sin indexar."""
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


class HomeV2Tests(TestCase):
    def get(self, path="/v2/"):
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        return response, response.content.decode()

    def test_v2_renders_with_its_template(self):
        response, _ = self.get()
        self.assertTemplateUsed(response, "core/home_v2.html")

    def test_v2_is_never_indexed(self):
        _, html = self.get()
        self.assertIn('<meta name="robots" content="noindex, nofollow">', html)

    def test_v2_assets_are_local_and_script_has_nonce(self):
        _, html = self.get()
        self.assertRegex(html, r'<link rel="stylesheet" href="/static/css/v2\.css">')
        self.assertRegex(html, r'<script src="/static/js/v2\.js" defer nonce="[^"]+"></script>')

    def test_v2_keeps_the_same_texts(self):
        """Nuestra información manda: el contenido es el de textos-v1.md, igual que en /."""
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

    def test_drawings_are_decorative(self):
        _, html = self.get()
        for svg_class in ("v2-plan", "v2-stage"):
            self.assertRegex(html, rf'<(?:figure|div) class="{svg_class}[^"]*" aria-hidden="true">')

    def test_nav_stays_on_v2(self):
        _, html = self.get()
        self.assertIn('href="/v2/#nosotros"', html)
        self.assertNotIn('href="/#nosotros"', html)

    def test_cta_tab_still_deferred(self):
        configure(whatsapp="912345678")
        _, html = self.get()
        self.assertIn("cta-tab--deferred", html)

    def test_home_v1_untouched(self):
        _, html = self.get("/")
        self.assertNotIn("v2.css", html)
        self.assertNotIn("v2.js", html)
        self.assertNotIn('name="robots"', html)
        self.assertIn('href="/#nosotros"', html)

    def test_v2_not_in_sitemap(self):
        xml = self.client.get("/sitemap.xml").content.decode()
        self.assertNotIn("/v2/", xml)


class V2StaticTests(SimpleTestCase):
    def read(self, relative):
        return (Path(settings.BASE_DIR) / "static" / relative).read_text(encoding="utf-8")

    def test_v2_js_under_budget(self):
        self.assertLess(len(self.read("js/v2.js").encode()), 20 * 1024)

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
