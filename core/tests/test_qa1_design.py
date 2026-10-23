"""Ronda 1 de QA (diseño): filtro de WhatsApp visible, páginas de error y CSS/JS/guía."""
import re
import tempfile
from pathlib import Path

from django.conf import settings
from django.template import Context, Template
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings
from django.urls import get_resolver

from core.templatetags.site_tags import wa_display
from core.tests.test_base import configure


class WaDisplayFilterTests(SimpleTestCase):
    def test_formats_every_accepted_chilean_format(self):
        for raw in ("912345678", "+56 9 1234 5678", "56912345678", "9 1234-5678"):
            self.assertEqual(wa_display(raw), "+56 9 1234 5678", raw)

    def test_invalid_number_is_returned_untouched(self):
        self.assertEqual(wa_display("pendiente"), "pendiente")
        self.assertEqual(wa_display(""), "")
        self.assertEqual(wa_display(None), "")

    def test_usable_from_a_template(self):
        html = Template("{% load site_tags %}{{ n|wa_display }}").render(Context({"n": "912345678"}))
        self.assertEqual(html, "+56 9 1234 5678")


@override_settings(ROOT_URLCONF="core.tests.urls", MEDIA_ROOT=tempfile.mkdtemp())
class FooterContactTests(TestCase):
    def test_footer_shows_formatted_whatsapp_with_unchanged_href(self):
        configure(whatsapp="912345678")
        html = self.client.get("/base/").content.decode()
        footer = html[html.index("<footer"):]
        self.assertIn("+56 9 1234 5678</a>", footer)
        self.assertIn("https://wa.me/56912345678?", footer)

    def test_footer_email_can_break_after_the_at_sign(self):
        configure(email="contacto@schobras.cl")
        html = self.client.get("/base/").content.decode()
        footer = html[html.index("<footer"):]
        self.assertIn("contacto@<wbr>schobras.cl</a>", footer)
        self.assertIn('href="mailto:contacto@schobras.cl"', footer)


@override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver"])
class ErrorPageLayoutTests(TestCase):
    def test_404_heading_and_text_live_in_a_spaced_block(self):
        html = self.client.get("/no-existe/").content.decode()
        self.assertRegex(html, r'<header class="error-page">\s*<p class="label">SCHOBRAS.CL</p>\s*<h1')

    def test_500_heading_and_text_live_in_a_spaced_block(self):
        handler = get_resolver().resolve_error_handler(500)
        html = handler(RequestFactory().get("/")).content.decode()
        self.assertRegex(html, r'<header class="error-page">\s*<p class="label">SCHOBRAS.CL</p>\s*<h1')


class StaticDesignTests(SimpleTestCase):
    def read(self, relative):
        return (Path(settings.BASE_DIR) / relative).read_text(encoding="utf-8")

    def rule(self, css, selector):
        match = re.search(re.escape(selector) + r"\s*\{([^}]*)\}", css)
        self.assertIsNotNone(match, selector)
        return match.group(1)

    def test_error_page_class_is_a_grid_with_gap(self):
        body = self.rule(self.read("static/css/site.css"), ".error-page")
        self.assertIn("display: grid", body)
        self.assertIn("gap:", body)

    def test_cota_start_draws_its_line_in_the_second_column(self):
        self.assertIn("grid-column: 2", self.rule(self.read("static/css/site.css"), ".cota--start::after"))

    def test_filter_chips_are_opaque_over_the_axes(self):
        self.assertIn("background: var(--color-white)", self.rule(self.read("static/css/site.css"), ".projects__chip"))

    def test_menu_open_makes_skip_link_inert(self):
        self.assertIn('main, footer, .cta-tab, .skip-link', self.read("static/js/site.js"))

    def test_site_js_under_budget(self):
        self.assertLess(len(self.read("static/js/site.js").encode()), 20 * 1024)

    def test_panel_declares_danger_token_and_guide_lists_it(self):
        panel = self.read("static/css/panel.css")
        self.assertIn("--color-danger: #8a1f1f;", panel)
        self.assertNotIn("--color-error", panel)
        self.assertRegex(self.read("docs/06-frontend/guia-visual.md"), r"`--color-danger` \| `#8A1F1F`")

    def test_panel_row_actions_forms_are_flex_items_with_centered_nowrap_buttons(self):
        css = self.read("static/css/panel.css")
        self.assertIn("white-space: nowrap", self.rule(css, ".btn"))
        self.assertIn("text-align: center", self.rule(css, ".btn"))
        self.assertRegex(css, r"\.row-actions > form \{ display: flex; \}")
        self.assertIn("flex: 1", self.rule(css, ".row-actions > form .btn"))

    def test_panel_file_input_is_big_and_styled(self):
        css = self.read("static/css/panel.css")
        body = self.rule(css, '.form input[type="file"]')
        self.assertIn("min-height: 48px", body)
        self.assertIn("width: 100%", body)
        button = self.rule(css, '.form input[type="file"]::file-selector-button')
        self.assertIn("border: 2px solid var(--color-anthracite)", button)
        self.assertIn("min-height: 44px", button)
        self.assertIn("font-weight: 600", button)

    def test_panel_form_controls_use_site_colours(self):
        css = self.read("static/css/panel.css")
        self.assertIn("accent-color: var(--color-anthracite)", self.rule(css, ".form"))
        self.assertIn("background: var(--color-white)", self.rule(css, ".form select, .form input[type=\"number\"], .form textarea"))
