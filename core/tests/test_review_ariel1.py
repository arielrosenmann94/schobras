"""Revisión humana de Ariel, ronda 1: fondo sin ejes interiores (A1) y pestaña lateral de CTA (A2)."""
import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase, TestCase

from core.tests.test_base import configure
from projects.models import Project, ProjectPhoto
from projects.tests.test_models import make_image, make_project


def read(relative):
    return (Path(settings.BASE_DIR) / relative).read_text(encoding="utf-8")


def plan_block(css):
    """Bloque «Plano» de site.css: desde su título hasta la sección siguiente."""
    start = css.index("/* ── Plano:")
    return css[start:css.index("/* ──", start + 1)]


class AxesBackgroundTests(SimpleTestCase):
    def test_no_interior_axes_declared(self):
        block = plan_block(read("static/css/site.css"))
        for interior in ("25% 0", "50% 0 / 1px", "75% 0"):
            self.assertNotIn(interior, block)
        self.assertNotIn("linear-gradient", block)

    def test_frame_keeps_its_two_borders(self):
        self.assertIn("border-inline: 1px solid", plan_block(read("static/css/site.css")))

    def test_frame_sits_outside_the_content(self):
        """El marco es medio margen más ancho que el contenido por lado: nunca toca una letra."""
        block = plan_block(read("static/css/site.css"))
        rule = re.search(r"body::before,\s*\.axes::before\s*\{([^}]*)\}", block).group(1)
        self.assertNotIn("100% - 2 * var(--gutter)", rule)
        # Mismo ancho y margen izquierdo que .container, más medio margen por lado.
        self.assertIn("- var(--gutter) / 2", rule)
        self.assertIn("+ var(--gutter));", rule)
        self.assertIn("var(--gutter-end)", rule)


def rule(css, selector):
    match = re.search(r"(?:^|\n)" + re.escape(selector) + r"\s*\{([^}]*)\}", css)
    assert match, selector
    return match.group(1)


class CtaTabStyleTests(SimpleTestCase):
    def setUp(self):
        self.css = read("static/css/site.css")

    def test_floating_button_is_gone(self):
        for relative in ("static/css/site.css", "static/js/site.js", "templates/includes/whatsapp.html"):
            self.assertNotIn("whatsapp-float", read(relative), relative)

    def test_tab_is_fixed_to_the_right_edge_and_centered(self):
        body = rule(self.css, ".cta-tab")
        self.assertIn("position: fixed", body)
        self.assertIn("top: 50%", body)
        self.assertIn("right: env(safe-area-inset-right, 0px)", body)
        self.assertIn("transform: translateY(-50%)", body)
        self.assertNotIn("transition", body)

    def test_tab_colors_follow_the_guide(self):
        body = rule(self.css, ".cta-tab")
        self.assertIn("background: var(--color-anthracite)", body)
        self.assertIn("color: var(--color-white)", body)
        self.assertNotRegex(body, r"background[^;]*bronze")
        self.assertIn("var(--color-bronze)", body)

    def test_tab_is_at_least_44px_wide(self):
        self.assertIn("--tab-width: 2.75rem", self.css)
        self.assertIn("width: var(--tab-width)", rule(self.css, ".cta-tab"))

    def test_text_is_vertical_reading_bottom_up(self):
        body = rule(self.css, ".cta-tab__text")
        self.assertIn("writing-mode: vertical-rl", body)
        self.assertIn("transform: rotate(180deg)", body)

    def test_tab_stays_below_the_header_and_its_menu(self):
        header = int(re.search(r"z-index:\s*(\d+)", rule(self.css, ".site-header")).group(1))
        tab = int(re.search(r"z-index:\s*(\d+)", rule(self.css, ".cta-tab")).group(1))
        self.assertLess(tab, header)
        self.assertIn("html.menu-open .cta-tab { visibility: hidden; }", self.css)
        self.assertIn("main, footer, .cta-tab, .skip-link", read("static/js/site.js"))

    def test_focus_and_hover_are_visible(self):
        self.assertRegex(self.css, r"\.cta-tab:focus-visible\s*\{\s*outline-color: var\(--color-bronze\)")
        self.assertIn(".cta-tab:hover", self.css)

    def test_content_leaves_the_tab_lane_free(self):
        lane = rule(self.css, ".has-cta-tab")
        self.assertIn("--gutter-end: max(var(--gutter), var(--tab-width)", lane)
        self.assertIn("env(safe-area-inset-right, 0px)", lane)
        container = rule(self.css, ".container")
        self.assertIn("var(--gutter-end)", container)
        for wall in (".home-grid > .home-vision", ".home-pillar--main", ".home-step--final"):
            self.assertIn("calc(var(--gutter-end) * -1)", rule(self.css, wall), wall)


class CtaTabPagesTests(TestCase):
    def test_detail_tab_prefills_the_project_message(self):
        configure(whatsapp="912345678")
        project = make_project(title="Casa Chicureo", status=Project.Status.PUBLISHED)
        ProjectPhoto.objects.create(project=project, image=make_image())
        html = self.client.get(project.get_absolute_url()).content.decode()
        self.assertRegex(html, r'<a class="cta-tab" href="https://wa\.me/56912345678\?text=Hola%2C%20vi%20el%20proyecto%20Casa%20Chicureo%20y%20quiero')

    def test_home_with_phone_and_email_keeps_contact_block_without_tab(self):
        configure(phone="+56 2 2345 6789", email="oficina@example.com")
        html = self.client.get("/").content.decode()
        self.assertNotIn("cta-tab", html)
        contact = re.search(r'<section[^>]*id="contacto".*?</section>', html, re.S).group(0)
        self.assertIn('href="tel:+56223456789"', contact)
        self.assertIn('href="mailto:oficina@example.com"', contact)
        self.assertIn("Conversemos tu proyecto", html)
