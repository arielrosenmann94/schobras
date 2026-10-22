from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings
from django.urls import get_resolver, reverse

from accounts.models import User


@override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver"])
class ServerErrorPageTests(SimpleTestCase):
    """SimpleTestCase: cualquier consulta a la BD haría fallar la prueba."""

    def test_500_is_standalone_and_in_spanish(self):
        handler = get_resolver().resolve_error_handler(500)
        response = handler(RequestFactory().get("/proyectos/"))
        self.assertEqual(response.status_code, 500)
        html = response.content.decode()
        self.assertIn('<html lang="es-CL">', html)
        self.assertIn("<title>Algo falló | SCHOBRAS.CL</title>", html)
        self.assertIn("Algo falló de nuestro lado", html)
        self.assertIn("Vuelve a intentarlo en unos minutos.", html)
        self.assertIn('href="/static/css/site.css"', html)
        self.assertIn('<a class="btn btn--primary" href="/">Volver al inicio</a>', html)
        self.assertNotRegex(html, "sty" + 'le="')


@override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver"])
class PermissionDeniedPageTests(TestCase):
    def test_editor_sees_spanish_403_in_settings(self):
        editor = User.objects.create_user(username="claudia", password="x-clave-123")
        self.client.force_login(editor)
        response = self.client.get(reverse("panel:settings"))
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "403.html")
        self.assertContains(response, "No tienes acceso a esta página", status_code=403)
        self.assertContains(response, f'href="{reverse("panel:home")}"', status_code=403)
        self.assertNotContains(response, "Forbidden", status_code=403)
