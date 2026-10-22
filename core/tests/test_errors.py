from django.core.exceptions import SuspiciousOperation
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings
from django.urls import get_resolver, reverse

from accounts.models import User
from projects.models import Category, Project


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
class BadRequestPageTests(TestCase):
    """QA-1.13: el 400 salía como "Bad Request (400)" en inglés y sin marca."""

    def test_400_is_standalone_and_in_spanish(self):
        handler = get_resolver().resolve_error_handler(400)
        response = handler(RequestFactory().post("/panel/"), SuspiciousOperation())
        self.assertEqual(response.status_code, 400)
        html = response.content.decode()
        self.assertIn('<html lang="es-CL">', html)
        self.assertIn('<meta name="robots" content="noindex">', html)
        self.assertIn("SCHOBRAS", html)
        self.assertIn("Algo salió mal con el envío", html)
        self.assertIn("Si subías fotos, sube de a menos.", html)
        self.assertIn('href="/static/css/site.css"', html)
        self.assertNotIn("Bad Request", html)
        self.assertNotRegex(html, "sty" + 'le="')


@override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver"])
class TooManyFilesTests(TestCase):
    def test_more_than_100_photos_shows_branded_400(self):
        editor = User.objects.create_user(username="claudia", password="x-clave-123")
        category = Category.objects.create(name="Casas")
        project = Project.objects.create(
            title="Casa",
            category=category,
            intervention_type="new_build",
            commune="Colina",
            region="metropolitana",
        )
        self.client.force_login(editor)
        files = [SimpleUploadedFile(f"f{i}.jpg", b"x", "image/jpeg") for i in range(101)]
        with self.assertLogs("django.security", level="ERROR"):
            response = self.client.post(
                reverse("panel:project_photos", args=[project.pk]), {"images": files}
            )
        self.assertContains(response, "Si subías fotos, sube de a menos.", status_code=400)


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
