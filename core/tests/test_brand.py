import re
from pathlib import Path

from django.conf import settings

from django.template.loader import render_to_string
from django.test import RequestFactory, TestCase, override_settings
from django.urls import get_resolver, reverse

from accounts.models import User
from core.templatetags.site_tags import brand_name

WORDMARK = '<span class="brand-name"><span class="brand__sch">SCH</span>obras'


def visible_plain_brand(html):
    """Apariciones de SCHOBRAS (en cualquier caja) en texto visible sin la marca con estilo.

    No cuenta <head> (title, metas, JSON-LD), <script> ni atributos (aria-label, alt),
    donde la marca va como texto plano a propósito.
    """
    body = re.sub(r"<head>.*?</head>", "", html, flags=re.S)
    body = re.sub(r"<script.*?</script>", "", body, flags=re.S)
    body = re.sub(r'="[^"]*"', '=""', body)
    return re.findall(r"schobras", body, flags=re.I)


class BrandNameTagTests(TestCase):
    def test_brand_name_is_option_4(self):
        """Claudia eligió la opción 4 de /sch/ (2026-10-25): SCH en mayúsculas y bronce, obras en minúsculas."""
        self.assertEqual(brand_name(), f"{WORDMARK}.cl</span>")
        self.assertEqual(brand_name(domain=False), f"{WORDMARK}</span>")

    def test_home_section_02_says_schobras(self):
        html = self.client.get("/").content.decode()
        self.assertIn(f">Por qué {WORDMARK}</span></h2>", html)

    def test_brand_keeps_its_case_inside_uppercase_labels(self):
        css = (Path(settings.BASE_DIR) / "static" / "css" / "site.css").read_text(encoding="utf-8")
        self.assertIn(".brand-name { text-transform: none; }", css)

    def test_plain_text_brand_uses_the_same_case(self):
        """En title, metas, JSON-LD y aria-label la marca va sin estilo, pero con la misma caja."""
        html = self.client.get("/").content.decode()
        self.assertIn("<title>SCHobras.cl | ", html)
        self.assertIn('aria-label="SCHobras.cl, inicio"', html)
        self.assertIn('"name": "SCHobras.cl"', html)
        self.assertNotIn("SCHOBRAS", html)


@override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver"])
class BrandEverywhereTests(TestCase):
    """Ariel, 2026-10-23: en todo lugar visible donde diga SCHOBRAS, SCH va en bronce (que no se lea "sobras")."""

    def assert_branded(self, html, where):
        self.assertEqual(visible_plain_brand(html), [], where)
        self.assertIn(WORDMARK, html, where)

    def test_public_pages(self):
        for url in ("/", reverse("projects:list"), "/no-existe/"):
            with self.subTest(url=url):
                self.assert_branded(self.client.get(url).content.decode(), url)

    def test_403_page(self):
        request = RequestFactory().get("/")
        self.assert_branded(render_to_string("403.html", request=request), "403")

    def test_400_and_500_pages(self):
        from django.core.exceptions import SuspiciousOperation

        resolver = get_resolver()
        html_500 = resolver.resolve_error_handler(500)(RequestFactory().get("/")).content.decode()
        html_400 = resolver.resolve_error_handler(400)(RequestFactory().get("/"), SuspiciousOperation()).content.decode()
        self.assert_branded(html_500, "500")
        self.assert_branded(html_400, "400")

    def test_panel(self):
        self.assert_branded(self.client.get(reverse("panel:login")).content.decode(), "login")
        editor = User.objects.create_user("editora", "e@example.com", "pw-12345-x")
        self.client.force_login(editor)
        self.assert_branded(self.client.get(reverse("panel:home")).content.decode(), "panel")


class WordmarkNarrowScreenTests(TestCase):
    """D10-1: el encabezado se partía en dos filas a 360-368 px (también en el Samsung de Claudia)."""

    def test_wordmark_is_compact_and_never_wraps(self):
        css = (Path(settings.BASE_DIR) / "static" / "css" / "site.css").read_text(encoding="utf-8")
        rule = re.search(r"\n\.brand__word \{([^}]*)\}", css).group(1)
        self.assertIn("letter-spacing: 0.04em;", rule)
        self.assertIn("white-space: nowrap;", rule)
