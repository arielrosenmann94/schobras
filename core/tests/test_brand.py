import re

from django.template.loader import render_to_string
from django.test import RequestFactory, TestCase, override_settings
from django.urls import get_resolver, reverse

from accounts.models import User
from core.templatetags.site_tags import brand_name

WORDMARK = '<span class="brand__sch">SCH</span>OBRAS'


def visible_plain_brand(html):
    """Apariciones de SCHOBRAS en texto visible sin el SCH en bronce.

    No cuenta <head> (title, metas, JSON-LD), <script> ni atributos (aria-label, alt),
    donde la marca va como texto plano a propósito.
    """
    body = re.sub(r"<head>.*?</head>", "", html, flags=re.S)
    body = re.sub(r"<script.*?</script>", "", body, flags=re.S)
    body = re.sub(r'="[^"]*"', '=""', body)
    return re.findall(r"SCHOBRAS", body)


class BrandNameTagTests(TestCase):
    def test_brand_name_separates_sch(self):
        self.assertEqual(brand_name(), f"{WORDMARK}.CL")
        # Junto solo en el dominio; el nombre suelto va separado (Ariel, 2026-10-23).
        self.assertEqual(brand_name(domain=False), '<span class="brand__sch">SCH</span> OBRAS')

    def test_home_section_02_says_sch_obras_separated(self):
        html = self.client.get("/").content.decode()
        self.assertIn('>Por qué <span class="brand__sch">SCH</span> OBRAS</h2>', html)


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
