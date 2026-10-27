import json
import re
import tempfile

from django.test import TestCase, override_settings
from django.urls import reverse

from core.models import SiteSettings
from projects.models import Project, ProjectPhoto
from projects.tests.test_models import make_image, make_project

HOME_TITLE = "SCHobras.cl | Arquitectura y construcción en RM, Valparaíso y O'Higgins"
HOME_DESCRIPTION = (
    "Diseñamos y construimos proyectos residenciales, comerciales e industriales. "
    "Si construyes con nosotros, el proyecto de arquitectura se descuenta del presupuesto de obra."
)
AREAS = [
    "Región Metropolitana de Santiago",
    "Región de Valparaíso",
    "Región del Libertador General Bernardo O'Higgins",
]


def publish(title):
    project = make_project(title=title, status=Project.Status.PUBLISHED)
    ProjectPhoto.objects.create(project=project, image=make_image(), alt_text=f"Fachada de {title}")
    return project


def jsonld(response):
    html = response.content.decode()
    match = re.search(r'<script type="application/ld\+json" nonce="([^"]+)">(.*?)</script>', html, re.S)
    assert match, "sin JSON-LD con nonce"
    return match.group(1), json.loads(match.group(2))


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class SeoTests(TestCase):
    def test_robots(self):
        with override_settings(ADMIN_URL="gestion-secreta/"):
            response = self.client.get("/robots.txt")
        self.assertEqual(response["Content-Type"].split(";")[0], "text/plain")
        body = response.content.decode()
        self.assertIn("Disallow: /panel/", body)
        self.assertRegex(body, r"(?m)^Sitemap: http://testserver/sitemap\.xml$")
        self.assertNotIn("gestion-secreta", body)

    @override_settings(SEARCH_INDEXING=False)
    def test_robots_disallows_everything_while_indexing_off(self):
        body = self.client.get("/robots.txt").content.decode()
        self.assertRegex(body, r"(?m)^Disallow: /$")
        self.assertNotIn("Sitemap:", body)

    @override_settings(SEARCH_INDEXING=False)
    def test_noindex_header_while_indexing_off(self):
        for path in ("/", "/proyectos/", "/no-existe/"):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path)["X-Robots-Tag"], "noindex, nofollow")

    @override_settings(SEARCH_INDEXING=True)
    def test_no_noindex_header_while_indexing_on(self):
        self.assertNotIn("X-Robots-Tag", self.client.get("/"))

    def test_sitemap_published_only(self):
        visible = publish("Casa Visible")
        make_project(title="Borrador Oculto")
        sin_fotos = make_project(title="Sin Fotos", status=Project.Status.PUBLISHED)
        body = self.client.get("/sitemap.xml").content.decode()
        self.assertIn("http://testserver/", body)
        self.assertIn("http://testserver" + reverse("projects:list"), body)
        self.assertIn("http://testserver" + visible.get_absolute_url(), body)
        self.assertNotIn("borrador-oculto", body)
        self.assertNotIn(sin_fotos.slug, body)

    def test_jsonld_home(self):
        nonce, data = jsonld(self.client.get("/"))
        self.assertTrue(nonce)
        self.assertEqual(data["@type"], "GeneralContractor")
        self.assertEqual(data["legalName"], "Constructora Schonffeldt SpA")
        self.assertEqual(data["taxID"], "77.897.204-2")
        self.assertEqual([a["name"] for a in data["areaServed"]], AREAS)
        self.assertNotIn("address", data)
        self.assertNotIn("telephone", data)
        self.assertNotIn("email", data)

    def test_jsonld_contact_only_when_configured(self):
        settings_obj = SiteSettings.load()
        settings_obj.phone = "+56 2 2345 6789"
        settings_obj.email = "hola@schobras.cl"
        settings_obj.save()
        _, data = jsonld(self.client.get("/"))
        self.assertEqual(data["telephone"], "+56 2 2345 6789")
        self.assertEqual(data["email"], "hola@schobras.cl")

    def test_jsonld_escapes_script_close(self):
        settings_obj = SiteSettings.load()
        settings_obj.phone = "</script><b>"
        settings_obj.save()
        html = self.client.get("/").content.decode()
        self.assertNotIn("</script><b>", html)
        self.assertIn("\\u003C/script\\u003E", html)

    def test_titles(self):
        home = self.client.get("/").content.decode()
        self.assertIn(f"<title>{HOME_TITLE}</title>", home)
        self.assertIn('property="og:title"', home)
        self.assertIn(f'<meta name="description" content="{HOME_DESCRIPTION}">', home)
        self.assertIn(f'<meta property="og:description" content="{HOME_DESCRIPTION}">', home)
        project = publish("Casa Chicureo")
        detail = self.client.get(project.get_absolute_url()).content.decode()
        self.assertIn("<title>Casa Chicureo en Colina | SCHobras.cl</title>", detail)

    def test_header_current_uses_resolved_url(self):
        project = publish("Casa Actual")
        current = 'href="%s" aria-current="page"' % reverse("projects:list")
        self.assertIn(current, self.client.get(reverse("projects:list")).content.decode())
        self.assertIn(current, self.client.get(project.get_absolute_url()).content.decode())
        self.assertNotIn(current, self.client.get("/").content.decode())


@override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver"])
class NotFoundTests(TestCase):
    def test_404_branded(self):
        response = self.client.get("/no-existe/")
        self.assertEqual(response.status_code, 404)
        html = response.content.decode()
        self.assertIn("Esta página no existe", html)
        self.assertIn("Puede que el enlace esté mal escrito o que el proyecto ya no esté publicado.", html)
        self.assertIn("Volver al inicio", html)
        self.assertIn("SCHobras", html)
        self.assertIn(f'href="{reverse("core:home")}"', html)
        self.assertEqual(SiteSettings.objects.count(), 0)

    def test_404_commercial_block_with_whatsapp(self):
        site = SiteSettings.load()
        site.whatsapp = "912345678"
        site.save()
        html = self.client.get("/no-existe/").content.decode()
        closing = html[html.index('class="wall error-cta"'):html.index("</section>", html.index('class="wall error-cta"'))]
        self.assertIn("Tu proyecto sí puede existir", closing)
        self.assertIn("Diseñamos y construimos", closing)
        self.assertRegex(closing, r'<a class="btn btn--primary" href="https://wa\.me/56912345678\?text=[^"]*"[^>]*>Cotiza tu proyecto por WhatsApp</a>')
        self.assertIn("Volver al inicio", html)

    def test_404_without_whatsapp_has_no_commercial_button(self):
        html = self.client.get("/no-existe/").content.decode()
        self.assertNotIn("wa.me", html)
        self.assertNotIn("Cotiza tu proyecto por WhatsApp", html)
        self.assertIn("Volver al inicio", html)
