"""Página /sch/: formas de escribir SCHOBRAS para que no se lea "sobras" (para decidir, sin indexar)."""
import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase, TestCase

from core.tests.test_base import configure
from core.views import BRAND_OPTIONS


class BrandOptionsPageTests(TestCase):
    def get(self):
        response = self.client.get("/sch/")
        self.assertEqual(response.status_code, 200)
        return response, response.content.decode()

    def test_renders_its_template(self):
        response, _ = self.get()
        self.assertTemplateUsed(response, "core/sch.html")

    def test_never_indexed_nor_in_sitemap(self):
        _, html = self.get()
        self.assertIn('<meta name="robots" content="noindex, nofollow">', html)
        self.assertNotIn("/sch/", self.client.get("/sitemap.xml").content.decode())

    def test_not_linked_from_the_menu(self):
        html = self.client.get("/").content.decode()
        self.assertNotIn('href="/sch/"', html)

    def test_assets_are_local_and_script_has_nonce(self):
        _, html = self.get()
        self.assertIn('<link rel="stylesheet" href="/static/css/sch.css">', html)
        self.assertRegex(html, r'<script src="/static/js/sch\.js" defer nonce="[^"]+"></script>')

    def test_every_option_is_numbered_and_shown_three_ways(self):
        _, html = self.get()
        self.assertEqual(len(BRAND_OPTIONS), 12)
        for number in range(1, len(BRAND_OPTIONS) + 1):
            with self.subTest(option=number):
                self.assertIn(f'id="opcion-{number}"', html)
                self.assertIn(f"Opción {number}: ", html)
                self.assertEqual(html.count(f'class="wm wm--{number}"'), 3)
                self.assertIn(f'data-sch-try="{number}"', html)

    def test_includes_claudias_proposal(self):
        """Claudia: SCH en mayúsculas y obras en minúsculas, quizá en el color del logo."""
        option = BRAND_OPTIONS[1]
        self.assertEqual((option["sch"], option["obras"]), ("SCH", "obras"))
        self.assertIn("Claudia", option["name"])
        _, html = self.get()
        self.assertIn('<span class="wm__sch">SCH</span><span class="wm__sep"></span><span class="wm__tail"><span class="wm__obras">obras</span>', html)

    def test_current_option_matches_the_site(self):
        """La opción 1 es la que hoy muestra la web: SCH en bronce + OBRAS.CL."""
        self.assertEqual(BRAND_OPTIONS[0]["sch"] + BRAND_OPTIONS[0]["obras"] + BRAND_OPTIONS[0]["cl"], "SCHOBRAS.CL")

    def test_one_h1_and_no_inline_styles(self):
        configure(whatsapp="912345678")
        _, html = self.get()
        self.assertEqual(html.count("<h1"), 1)
        self.assertNotRegex(html, r"\sstyle\s*=")


class BrandOptionsStaticTests(SimpleTestCase):
    def read(self, relative):
        return (Path(settings.BASE_DIR) / "static" / relative).read_text(encoding="utf-8")

    def test_css_uses_only_brand_tokens(self):
        css = self.read("css/sch.css")
        self.assertNotRegex(css, r"#[0-9a-fA-F]{3,6}\b")
        self.assertNotRegex(css, r"\brgba?\(|\bhsla?\(")

    def test_try_button_hidden_without_js(self):
        self.assertIn('html:not(.js) .sch-option__try { display: none; }', self.read("css/sch.css"))

    def test_js_under_budget_and_only_touches_this_page(self):
        js = self.read("js/sch.js")
        self.assertLess(len(js.encode()), 20 * 1024)
        self.assertIn("[data-sch-try]", js)
        self.assertNotRegex(js, r"localStorage|fetch\(|XMLHttpRequest")

    def test_variants_cover_every_option(self):
        css = self.read("css/sch.css")
        defined = {int(n) for n in re.findall(r"\.wm--(\d+)\b", css)}
        # La 3 no necesita reglas: es solo la caja de las letras, en un color.
        self.assertEqual(defined | {3}, set(range(1, len(BRAND_OPTIONS) + 1)))
