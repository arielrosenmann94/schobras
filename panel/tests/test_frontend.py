import re

from django.contrib.staticfiles import finders
from django.test import TestCase
from django.urls import reverse

from accounts.models import User


class PanelScriptTests(TestCase):
    """QA-1.12: un doble clic en Guardar o Subir fotos creaba duplicados."""

    def test_panel_pages_load_panel_js_with_nonce(self):
        user = User.objects.create_user(username="claudia", password="x-clave-123")
        self.client.force_login(user)
        for url in [reverse("panel:home"), reverse("panel:project_create"), reverse("panel:login")]:
            with self.subTest(url=url):
                response = self.client.get(url, follow=True)
                match = re.search(
                    r'<script src="/static/js/panel\.js" defer nonce="([^"]+)"></script>',
                    response.content.decode(),
                )
                self.assertIsNotNone(match, "falta panel.js con defer y nonce")
                self.assertIn(f"'nonce-{match.group(1)}'", response["Content-Security-Policy"])

    def test_panel_js_disables_submit_buttons(self):
        path = finders.find("js/panel.js")
        self.assertIsNotNone(path)
        with open(path, encoding="utf-8") as script:
            source = script.read()
        self.assertIn('addEventListener("submit"', source)
        self.assertIn("disabled = true", source)
        # Al volver con el botón "atrás" (bfcache) los botones se reactivan.
        self.assertIn('addEventListener("pageshow"', source)
