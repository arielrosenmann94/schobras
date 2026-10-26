"""Política de privacidad (/privacidad/) y pie legal: derechos reservados y crédito de desarrollo (Ariel, 2026-10-25)."""
import re

from django.test import TestCase

from core.tests.test_base import configure


class PrivacyPageTests(TestCase):
    def get(self):
        response = self.client.get("/privacidad/")
        self.assertEqual(response.status_code, 200)
        return response, response.content.decode()

    def test_renders_its_template_with_title(self):
        response, html = self.get()
        self.assertTemplateUsed(response, "core/privacy.html")
        self.assertIn("<title>Política de privacidad | SCHobras.cl</title>", html)
        self.assertEqual(html.count("<h1"), 1)
        self.assertNotRegex(html, r"\sstyle\s*=")

    def test_states_what_whatsapp_is_for_and_that_data_is_not_shared(self):
        """Texto exacto de docs/02-producto/textos-v1.md §Política de privacidad."""
        _, html = self.get()
        self.assertIn("El contacto por WhatsApp es exclusivo para cotizar y consultar por proyectos de arquitectura y construcción.", html)
        self.assertIn("No compartimos tus datos con nadie.", html)
        self.assertIn("Los usamos solo para la comunicación comercial sobre el proyecto que consultaste.", html)
        self.assertIn("Constructora Schonffeldt SpA", html)

    def test_rights_point_to_the_configured_email(self):
        configure(email="oficina@schobras.cl")
        _, html = self.get()
        self.assertIn('href="mailto:oficina@schobras.cl"', html)

    def test_without_email_rights_point_to_whatsapp(self):
        configure(whatsapp="912345678")
        _, html = self.get()
        self.assertNotIn("mailto:", html[html.index("<main"):html.index("<footer")])
        self.assertIn("https://wa.me/56912345678", html)

    def test_listed_in_sitemap(self):
        self.assertIn("/privacidad/", self.client.get("/sitemap.xml").content.decode())


class FooterLegalTests(TestCase):
    def footer(self):
        html = self.client.get("/").content.decode()
        return html[html.index("<footer"):]

    def test_rights_reserved_and_privacy_link(self):
        footer = self.footer()
        self.assertRegex(footer, r"© \d{4} Constructora Schonffeldt SpA\. Todos los derechos reservados\.")
        self.assertIn('<a href="/privacidad/">Política de privacidad</a>', footer)

    def test_developer_credit_links_to_ariels_site(self):
        footer = self.footer()
        link = re.search(r'<a [^>]*href="https://arielrosenmann\.com/"[^>]*>arielrosenmann\.com</a>', footer)
        self.assertIsNotNone(link)
        self.assertIn('target="_blank"', link.group(0))
        self.assertIn('rel="noopener"', link.group(0))
        self.assertIn("Desarrollado por", footer)
