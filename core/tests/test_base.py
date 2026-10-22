import re
import tempfile

from django.test import TestCase, override_settings
from django.utils import timezone

from core.models import SiteSettings
from projects.models import Project, ProjectPhoto
from projects.tests.test_models import make_image, make_project


def configure(**fields):
    settings_obj = SiteSettings.load()
    for name, value in fields.items():
        setattr(settings_obj, name, value)
    settings_obj.save()


@override_settings(ROOT_URLCONF="core.tests.urls", MEDIA_ROOT=tempfile.mkdtemp())
class BaseTemplateTests(TestCase):
    def get(self, url="/base/"):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        return response, response.content.decode()

    def test_no_whatsapp_no_button(self):
        _, html = self.get()
        self.assertNotIn("wa.me", html)
        self.assertNotIn("Escríbenos por WhatsApp", html)

    def test_whatsapp_button_with_aria_label(self):
        configure(whatsapp="+56 9 1234 5678")
        _, html = self.get()
        self.assertIn("https://wa.me/56912345678", html)
        self.assertIn('aria-label="Escríbenos por WhatsApp"', html)
        self.assertRegex(html, r'<a[^>]*rel="noopener"[^>]*aria-label="Escríbenos por WhatsApp"')

    def test_whatsapp_default_message(self):
        configure(whatsapp="912345678")
        _, html = self.get()
        self.assertIn("https://wa.me/56912345678?text=Hola%2C%20quiero%20conversar%20sobre%20un%20proyecto.", html)

    def test_whatsapp_message_block_overridden_by_child(self):
        configure(whatsapp="912345678")
        _, html = self.get("/hija/")
        self.assertIn("text=Hola%2C%20vi%20el%20proyecto%20Casa%20O%27Higgins%20y%20quiero", html)
        self.assertNotIn("conversar%20sobre%20un%20proyecto", html)

    def test_invalid_whatsapp_no_button(self):
        configure(whatsapp="123")
        _, html = self.get()
        self.assertNotIn("Escríbenos por WhatsApp", html)

    def test_menu_hides_projects_when_none(self):
        _, html = self.get()
        self.assertIn('href="/#nosotros"', html)
        self.assertIn('href="/#servicios"', html)
        self.assertIn('href="/#proceso"', html)
        self.assertNotIn('href="/proyectos/"', html)

    def test_menu_shows_projects_when_published(self):
        project = make_project(status=Project.Status.PUBLISHED)
        ProjectPhoto.objects.create(project=project, image=make_image())
        _, html = self.get()
        self.assertIn('href="/proyectos/"', html)

    def test_no_contact_no_contact_links(self):
        _, html = self.get()
        self.assertNotIn("#contacto", html)
        self.assertNotIn("mailto:", html)
        self.assertNotIn("tel:", html)

    def test_contact_in_menu_and_footer_email_only(self):
        configure(email="oficina@example.com")
        _, html = self.get()
        self.assertIn('href="/#contacto"', html)
        self.assertIn('href="mailto:oficina@example.com"', html)
        self.assertNotIn("tel:", html)
        self.assertNotIn("wa.me", html)

    def test_footer_phone_link(self):
        configure(phone="+56 2 2345 6789")
        _, html = self.get()
        self.assertIn('href="tel:+56223456789"', html)

    def test_footer_legal_name_no_rut(self):
        _, html = self.get()
        footer = html[html.index("<footer"):]
        self.assertIn("Constructora Schonffeldt SpA", footer)
        for region in ("Región Metropolitana", "Región de Valparaíso", "Región de O'Higgins"):
            self.assertIn(region, footer)
        self.assertIn(str(timezone.localdate().year), footer)
        self.assertNotIn("RUT", html)

    def test_skip_link_and_landmarks(self):
        _, html = self.get()
        self.assertIn('href="#contenido"', html)
        self.assertIn("<header", html)
        self.assertIn('<nav aria-label="Principal"', html)
        self.assertIn('<main id="contenido"', html)
        self.assertIn("<footer", html)
        first_link = re.search(r"<(a|button)\b[^>]*>", html).group(0)
        self.assertIn('href="#contenido"', first_link)

    def test_script_has_nonce(self):
        response, html = self.get()
        nonce = re.search(r"'nonce-([^']+)'", response["Content-Security-Policy"]).group(1)
        scripts = re.findall(r"<script\b[^>]*>", html)
        self.assertTrue(scripts)
        for tag in scripts:
            self.assertIn(f'nonce="{nonce}"', tag)

    def test_no_inline_styles(self):
        _, html = self.get()
        self.assertNotRegex(html, r"\sstyle\s*=")
        self.assertNotIn("<style", html)

    def test_isotype_inlined_with_rebars(self):
        _, html = self.get()
        self.assertIn('class="rebar"', html)
        self.assertNotIn("<?xml", html)

    def test_font_preloaded(self):
        _, html = self.get()
        self.assertRegex(html, r'<link rel="preload" href="[^"]*open-sans-latin-wght-normal\.woff2" as="font" type="font/woff2" crossorigin>')
