"""Ronda 2 de QA (diseño): correo del bloque de contacto y márgenes del panel."""
import re
import tempfile
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from core.tests.test_home import configure


def read(relative):
    return (Path(settings.BASE_DIR) / relative).read_text(encoding="utf-8")


def rule(css, selector):
    match = re.search(re.escape(selector) + r"\s*\{([^}]*)\}", css)
    return match.group(1) if match else ""


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ContactEmailTests(TestCase):
    def test_contact_email_uses_its_own_smaller_class(self):
        # QA-2.6: el correo se partía a mitad de palabra entre 768 y 920 px.
        configure(email="contacto@constructoraschonffeldt.cl")
        html = self.client.get(reverse("core:home")).content.decode()
        self.assertIn(
            '<span class="home-channel__value home-channel__value--email">'
            "contacto@<wbr>constructoraschonffeldt.cl</span>",
            html,
        )


class ContactEmailCssTests(SimpleTestCase):
    def test_email_value_font_is_smaller_than_other_channels(self):
        body = rule(read("static/css/site.css"), ".home-channel__value--email")
        self.assertRegex(body, r"font-size: clamp\(")
        self.assertNotIn("2.75rem", body)


class PanelSpacingTests(SimpleTestCase):
    def test_top_row_actions_leave_space_before_the_form(self):
        # QA-2.7: en Editar proyecto, Publicar quedaba pegado a "Nombre del proyecto" (0 px).
        body = rule(read("static/css/panel.css"), ".panel-main > .row-actions")
        self.assertIn("margin-bottom: calc(var(--space) * 3)", body)

    def test_file_button_goes_on_its_own_line_on_phones(self):
        # QA-2.8: a 360-390 px el texto del input se recortaba ("Ningún …cionado").
        self.assertRegex(
            read("static/css/panel.css"),
            r'@media \(max-width: 30em\) \{\s*\.form input\[type="file"\]::file-selector-button \{'
            r"[^}]*display: block;[^}]*width: 100%;",
        )
