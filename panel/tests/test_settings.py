from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from core.models import SiteSettings

PASSWORD = "clave-segura-123"
INVALID_WHATSAPP = "Número de WhatsApp no válido. Ejemplo: +56 9 1234 5678"
INVALID_PHONE = "Teléfono no válido. Ejemplo: +56 9 1234 5678"


class PanelSettingsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.editor = User.objects.create_user(username="claudia", password=PASSWORD)
        cls.admin = User.objects.create_user(
            username="ariel", password=PASSWORD, role=User.Role.ADMIN
        )

    def url(self):
        return reverse("panel:settings")

    def data(self, **extra):
        data = {
            "whatsapp": "+56 9 1234 5678",
            "phone": "+56 2 2345 6789",
            "email": "contacto@schobras.cl",
            "whatsapp_message": "Hola, quiero cotizar.",
        }
        data.update(extra)
        return data

    def test_url_path(self):
        self.assertEqual(self.url(), "/panel/configuracion/")

    def test_anonymous_redirects_to_login(self):
        response = self.client.get(self.url())
        self.assertEqual(response.status_code, 302)
        self.assertIn("/panel/ingresar/", response["Location"])

    def test_editor_gets_403(self):
        self.client.force_login(self.editor)
        self.assertEqual(self.client.get(self.url()).status_code, 403)
        self.assertEqual(self.client.post(self.url(), self.data()).status_code, 403)
        self.assertFalse(SiteSettings.objects.exists())

    def test_admin_sees_form(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Configuración del sitio")

    def test_admin_saves(self):
        self.client.force_login(self.admin)
        response = self.client.post(self.url(), self.data())
        self.assertRedirects(response, self.url(), fetch_redirect_response=False)
        settings_obj = SiteSettings.objects.get()
        self.assertEqual(settings_obj.whatsapp, "+56 9 1234 5678")
        self.assertEqual(settings_obj.email, "contacto@schobras.cl")
        follow = self.client.get(self.url())
        self.assertContains(follow, "Configuración guardada.")

    def test_blank_whatsapp_is_allowed(self):
        self.client.force_login(self.admin)
        response = self.client.post(self.url(), self.data(whatsapp=""))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(SiteSettings.objects.get().whatsapp, "")

    def test_invalid_whatsapp_form_error(self):
        self.client.force_login(self.admin)
        response = self.client.post(self.url(), self.data(whatsapp="123"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, INVALID_WHATSAPP)
        self.assertEqual(SiteSettings.load().whatsapp, "")

    def test_invalid_phone_form_error(self):
        self.client.force_login(self.admin)
        for phone in ("123", "pendiente", "+56 2 234"):
            with self.subTest(phone=phone):
                response = self.client.post(self.url(), self.data(phone=phone))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, INVALID_PHONE)
                self.assertFalse(SiteSettings.objects.exclude(phone="").exists())

    def test_valid_and_blank_phone_are_saved(self):
        self.client.force_login(self.admin)
        for phone in ("+56 (2) 2345-6789", "22345678", ""):
            with self.subTest(phone=phone):
                response = self.client.post(self.url(), self.data(phone=phone))
                self.assertEqual(response.status_code, 302)
                self.assertEqual(SiteSettings.objects.get().phone, phone)

    def test_help_and_error_ids_match_aria_describedby(self):
        self.client.force_login(self.admin)
        html = self.client.get(self.url()).content.decode()
        self.assertRegex(html, r'<input[^>]*aria-describedby="id_whatsapp_helptext"[^>]*id="id_whatsapp"')
        self.assertIn('<p class="help" id="id_whatsapp_helptext">', html)
        html = self.client.post(self.url(), self.data(whatsapp="123")).content.decode()
        self.assertRegex(
            html,
            r'<input[^>]*aria-describedby="id_whatsapp_helptext id_whatsapp_error"[^>]*id="id_whatsapp"',
        )
        self.assertIn(f'<p class="form-error" id="id_whatsapp_error" role="alert">{INVALID_WHATSAPP}</p>', html)

    def test_home_links_settings_for_admin_only(self):
        self.client.force_login(self.admin)
        self.assertContains(self.client.get(reverse("panel:home")), f'href="{self.url()}"')
        self.client.force_login(self.editor)
        self.assertNotContains(self.client.get(reverse("panel:home")), self.url())
