import re
import tempfile
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase, TestCase, override_settings

from core.models import SiteSettings
from core.templatetags.site_tags import email_brand, email_wbr
from projects.tests.test_views import publish

BRANDED = '<span class="email-brand">oficina@<wbr><span class="email-sch">sch</span>obras.cl</span>'


class EmailBrandFilterTests(SimpleTestCase):
    """Ariel, 2026-10-25: en el correo de la marca, "sch" y "obras" en colores distintos."""

    def test_wraps_sch_of_schobras_domain(self):
        self.assertEqual(email_brand("oficina@schobras.cl"), BRANDED)

    def test_case_insensitive_keeps_original_letters(self):
        self.assertEqual(
            email_brand("Oficina@SCHOBRAS.CL"),
            '<span class="email-brand">Oficina@<wbr><span class="email-sch">SCH</span>OBRAS.CL</span>',
        )

    def test_other_domains_unchanged(self):
        for email in ("oficina@claudiaarquitecta.cl", "schobras@gmail.com", "sin-arroba", ""):
            with self.subTest(email=email):
                self.assertEqual(email_brand(email), email_wbr(email))

    def test_escapes_user_data(self):
        html = email_brand('<b>"x"</b>@schobras.cl')
        self.assertNotIn("<b>", html)
        self.assertIn("&lt;b&gt;", html)
        self.assertIn('<span class="email-sch">sch</span>obras.cl', html)

    def test_sch_and_obras_never_split(self):
        self.assertNotRegex(email_brand("oficina@schobras.cl"), r"</span>\s+obras")


class EmailBrandCssTests(SimpleTestCase):
    def test_colors_per_background_with_aa_contrast(self):
        css = (Path(settings.BASE_DIR) / "static" / "css" / "site.css").read_text(encoding="utf-8")
        # Token nuevo: bronce profundo, 3,34:1 sobre cemento (texto grande en negrita).
        self.assertIn("--color-bronze-deep: color-mix(in srgb, var(--color-bronze) 40%, var(--color-anthracite));", css)
        self.assertRegex(css, r"\.home-channel \.email-sch \{[^}]*color: var\(--color-bronze-deep\);")
        self.assertRegex(css, r"\.home-channel:hover \.email-sch \{[^}]*color: var\(--color-white\);")
        self.assertRegex(css, r"\.site-footer__list \.email-brand,\s*\.btn--primary \.email-brand \{[^}]*color: var\(--color-cement\);")
        self.assertRegex(css, r"\.site-footer__list \.email-sch,\s*\.btn--primary \.email-sch \{[^}]*color: var\(--color-white\);")
        # El botón del detalle vive en un .wall, donde el botón principal es blanco.
        self.assertIn(".wall .btn--primary .email-brand { color: inherit; }", css)
        self.assertIn(".wall .btn--primary .email-sch { color: var(--color-bronze-deep); }", css)


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class EmailBrandTemplatesTests(TestCase):
    def configure(self, **fields):
        site = SiteSettings.load()
        for name, value in fields.items():
            setattr(site, name, value)
        site.save()

    def test_home_contact_and_footer(self):
        self.configure(email="oficina@schobras.cl", whatsapp="", phone="")
        html = self.client.get("/").content.decode()
        contact = html[html.index('id="contacto"'):html.index("<footer")]
        footer = html[html.index("<footer"):]
        self.assertIn(f'<span class="home-channel__value home-channel__value--email">{BRANDED}</span>', contact)
        self.assertIn(f'<a href="mailto:oficina@schobras.cl">{BRANDED}</a>', footer)

    def test_detail_closing_button(self):
        self.configure(email="oficina@schobras.cl", whatsapp="", phone="")
        project = publish("Casa Correo")
        html = self.client.get(project.get_absolute_url()).content.decode()
        self.assertIn(f'<a class="btn btn--primary" href="mailto:oficina@schobras.cl">Escríbenos a {BRANDED}</a>', html)
