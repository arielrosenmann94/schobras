from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, RequestFactory, SimpleTestCase, TestCase, override_settings
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
        self.assertContains(response, "No tienes acceso a esta página", status_code=403)
        self.assertContains(response, f'href="{reverse("panel:home")}"', status_code=403)
        self.assertNotContains(response, "Forbidden", status_code=403)

    def test_panel_403_uses_panel_layout(self):
        # QA-1.32: el 403 del panel mostraba cabecera, pie y WhatsApp públicos.
        editor = User.objects.create_user(username="claudia", password="x-clave-123")
        self.client.force_login(editor)
        response = self.client.get(reverse("panel:settings"))
        self.assertTemplateUsed(response, "panel/403.html")
        self.assertTemplateUsed(response, "panel/base.html")
        self.assertTemplateNotUsed(response, "base.html")
        self.assertContains(response, "SCHOBRAS.CL <span>Panel</span>", status_code=403)
        self.assertContains(response, "Esta sección es solo para quien administra el sitio.", status_code=403)
        self.assertContains(response, '<meta name="robots" content="noindex, nofollow">', status_code=403)

    def test_public_403_keeps_public_layout(self):
        handler = get_resolver().resolve_error_handler(403)
        request = RequestFactory().get("/proyectos/")
        request.user = AnonymousUser()
        response = handler(request, PermissionDenied())
        self.assertEqual(response.status_code, 403)
        html = response.content.decode()
        self.assertIn('<header class="error-page">', html)
        self.assertIn("No tienes acceso a esta página", html)
        self.assertNotIn("<span>Panel</span>", html)
        self.assertIn(f'href="{reverse("core:home")}"', html)


@override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver"])
class CsrfFailurePageTests(TestCase):
    """QA-2.2: el fallo de CSRF salía en inglés y sin marca (página por defecto de Django)."""

    def test_csrf_failure_is_branded_and_in_spanish(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post(
            reverse("panel:login"), {"username": "claudia", "password": "x-clave-123"}
        )
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "403_csrf.html")
        self.assertTemplateUsed(response, "panel/base.html")
        html = response.content.decode()
        self.assertIn('<html lang="es-CL">', html)
        self.assertIn("<title>La página caducó | SCHOBRAS.CL</title>", html)
        self.assertIn("SCHOBRAS.CL <span>Panel</span>", html)
        self.assertIn("<h1>La página caducó</h1>", html)
        self.assertIn("Por seguridad, el formulario venció. Vuelve al panel e inténtalo de nuevo.", html)
        self.assertIn(f'href="{reverse("panel:home")}">Volver al panel</a>', html)
        self.assertRegex(html, r'<script src="/static/js/panel\.js" defer nonce="[^"]+">')
        self.assertNotIn("Forbidden", html)
        self.assertNotIn("CSRF", html)
