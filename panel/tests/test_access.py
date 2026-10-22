import logging

from django.test import RequestFactory, TestCase
from django.urls import reverse

from accounts.models import User
from panel.client_ip import get_client_ip

PASSWORD = "clave-segura-123"


class QuietAxesMixin:
    """axes registra cada intento fallido; en las pruebas es solo ruido."""

    def setUp(self):
        super().setUp()
        logging.disable(logging.CRITICAL)
        self.addCleanup(logging.disable, logging.NOTSET)


class PanelAccessTests(QuietAxesMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.editor = User.objects.create_user(username="claudia", password=PASSWORD)
        cls.admin = User.objects.create_user(
            username="ariel", password=PASSWORD, role=User.Role.ADMIN
        )

    def test_anonymous_redirects_to_login(self):
        response = self.client.get(reverse("panel:home"))
        self.assertRedirects(
            response, "/panel/ingresar/?next=/panel/", fetch_redirect_response=False
        )

    def test_editor_enters_panel(self):
        self.client.force_login(self.editor)
        response = self.client.get(reverse("panel:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nuevo proyecto")
        self.assertContains(response, "Categorías")
        self.assertNotContains(response, "Configuración")

    def test_admin_sees_settings_button(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("panel:home"))
        self.assertContains(response, "Configuración")

    def test_login_flow_redirects_to_panel(self):
        response = self.client.post(
            reverse("panel:login"), {"username": "claudia", "password": PASSWORD}
        )
        self.assertRedirects(response, "/panel/", fetch_redirect_response=False)

    def test_is_admin_role(self):
        self.assertEqual(self.editor.role, User.Role.EDITOR)
        self.assertFalse(self.editor.is_admin_role)
        self.assertTrue(self.admin.is_admin_role)
        superuser = User.objects.create_superuser(username="root", password=PASSWORD)
        self.assertTrue(superuser.is_admin_role)

    def test_bad_credentials_spanish_message(self):
        response = self.client.post(
            reverse("panel:login"), {"username": "claudia", "password": "mala"}
        )
        self.assertContains(response, "Usuario o contraseña incorrectos.")

    def test_logout_post_only(self):
        self.client.force_login(self.editor)
        self.assertEqual(self.client.get(reverse("panel:logout")).status_code, 405)
        response = self.client.post(reverse("panel:logout"))
        self.assertRedirects(response, "/", fetch_redirect_response=False)
        self.assertEqual(self.client.get(reverse("panel:home")).status_code, 302)

    def test_axes_locks_after_5_failures(self):
        url = reverse("panel:login")
        for _ in range(5):
            self.client.post(url, {"username": "claudia", "password": "mala"})
        response = self.client.post(url, {"username": "claudia", "password": PASSWORD})
        self.assertContains(
            response,
            "Demasiados intentos. Vuelve a intentarlo en 30 minutos.",
            status_code=429,
        )
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_lockout_is_per_user_and_ip(self):
        url = reverse("panel:login")
        for _ in range(5):
            self.client.post(url, {"username": "claudia", "password": "mala"})
        self.client.post(url, {"username": "ariel", "password": PASSWORD})
        self.assertIn("_auth_user_id", self.client.session)


class ClientIpTests(TestCase):
    def test_uses_last_forwarded_entry(self):
        request = RequestFactory().get(
            "/", HTTP_X_FORWARDED_FOR="6.6.6.6, 203.0.113.9", REMOTE_ADDR="10.0.0.1"
        )
        self.assertEqual(get_client_ip(request), "203.0.113.9")

    def test_falls_back_to_remote_addr(self):
        request = RequestFactory().get("/", REMOTE_ADDR="10.0.0.1")
        self.assertEqual(get_client_ip(request), "10.0.0.1")
