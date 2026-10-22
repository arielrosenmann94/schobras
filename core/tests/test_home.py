import re
import tempfile

from django.db import connection
from django.test import SimpleTestCase, TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from core.models import SiteSettings
from core.templatetags.site_tags import tel_digits
from projects.models import Project, ProjectPhoto
from projects.tests.test_models import make_image, make_project

STEP_TITLES = [
    "Visita técnica y entrevista",
    "Presupuesto de arquitectura y especialidades",
    "Estudio y propuesta",
    "Ajustes en conjunto",
    "Proyecto y presupuesto de obra",
    "Construcción con descuento del proyecto",
]
REGIONS = ["Región Metropolitana", "Región de Valparaíso", "Región de O'Higgins"]


def configure(**fields):
    settings_obj = SiteSettings.load()
    for name, value in fields.items():
        setattr(settings_obj, name, value)
    settings_obj.save()


def publish(title, featured=True):
    project = make_project(title=title, status=Project.Status.PUBLISHED, is_featured=featured)
    ProjectPhoto.objects.create(project=project, image=make_image(), alt_text=f"Fachada de {title}")
    return project


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class HomeTests(TestCase):
    def get(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        return response.content.decode()

    def test_home_200_and_sections(self):
        html = self.get()
        self.assertIn("Visión", html)
        for title in STEP_TITLES:
            self.assertIn(title, html)
        for region in REGIONS:
            self.assertIn(region, html)
        # textos-v1.md escribe el sistema constructivo en minúscula.
        self.assertIn("madera, volcometal, paneles SIP", html)
        for anchor in ("nosotros", "servicios", "proceso"):
            self.assertIn(f'id="{anchor}"', html)

    def test_home_texts_from_textos_v1(self):
        html = self.get()
        eyebrow = re.search(r'<p class="label home-hero__eyebrow">(.*?)</p>', html, re.S).group(1)
        self.assertEqual(
            re.sub(r"<[^>]+>", "", eyebrow),
            "Arquitectura y construcción · Región Metropolitana · Valparaíso · O'Higgins",
        )
        self.assertRegex(html, r"<h1[^>]*>\s*Diseñamos y construimos tu proyecto.\s*</h1>")
        self.assertIn(
            "Si construyes con nosotros, el proyecto de arquitectura y los trámites municipales van sin costo adicional.",
            html,
        )
        for text in (
            "Arquitectura y trámites sin costo adicional",
            "Escuchamos e interpretamos",
            "Rigor técnico y normativo",
            "Diseño y especialidades",
            "Construcción</h3>",
            "Cómo construimos",
            "Gestión de permisos y trámites municipales.",
            "Llave en mano o con el nivel de terminaciones que necesites.",
        ):
            self.assertIn(text, html)

    def test_home_has_no_mision(self):
        html = self.get()
        self.assertNotIn("misión", html.lower())

    def test_25_years_attributed_to_professionals(self):
        html = self.get()
        self.assertRegex(html, r"grupo de profesionales[^.<]*con más de 25 años de experiencia")
        self.assertEqual(html.count("25 años"), 1)

    def test_single_h1_and_no_heading_jumps(self):
        html = self.get()
        levels = [int(level) for level in re.findall(r"<h([1-6])[\s>]", html)]
        self.assertEqual(levels.count(1), 1)
        self.assertEqual(levels[0], 1)
        for previous, current in zip(levels, levels[1:]):
            self.assertLessEqual(current - previous, 1, levels)

    def test_no_inline_styles_and_hero_without_reveal(self):
        html = self.get()
        self.assertNotRegex(html, r"\sstyle\s*=")
        hero = re.search(r'<section class="home-hero".*?</section>', html, re.S).group(0)
        self.assertNotIn("reveal", hero)
        self.assertIn('class="rebar"', hero)

    def test_featured_hidden_without_projects(self):
        html = self.get()
        self.assertNotIn('id="proyectos"', html)
        self.assertNotIn(f'href="{reverse("projects:list")}"', html)
        self.assertNotIn("Ver proyectos", html)

    def test_featured_hidden_when_none_is_featured(self):
        publish("Casa Pirque", featured=False)
        html = self.get()
        self.assertNotIn('id="proyectos"', html)
        self.assertIn("Ver proyectos", html)

    def test_draft_featured_not_shown(self):
        make_project(title="Casa Borrador", is_featured=True)
        html = self.get()
        self.assertNotIn("Casa Borrador", html)
        self.assertNotIn('id="proyectos"', html)

    def test_featured_max_6(self):
        projects = [publish(f"Casa {number}") for number in range(7)]
        html = self.get()
        self.assertIn('id="proyectos"', html)
        shown = [p for p in projects if f'href="{p.get_absolute_url()}"' in html]
        self.assertEqual(len(shown), 6)
        self.assertEqual(html.count('class="home-card"'), 6)
        self.assertIn("Ver todos los proyectos", html)

    def test_featured_card_link_and_image(self):
        project = publish("Casa Chicureo")
        html = self.get()
        self.assertIn(f'href="{project.get_absolute_url()}"', html)
        photo = project.cover_photo
        img = re.search(r'<img[^>]*src="' + re.escape(photo.image.url) + r'"[^>]*>', html).group(0)
        self.assertIn('alt="Fachada de Casa Chicureo"', img)
        self.assertIn('loading="lazy"', img)
        self.assertIn(f'width="{photo.image_width}" height="{photo.image_height}"', img)
        self.assertIn("srcset=", img)
        self.assertIn("Residencial", html)
        self.assertIn("Colina", html)

    def test_featured_queries_do_not_grow_with_projects(self):
        publish("Casa Uno")
        with CaptureQueriesContext(connection) as one:
            self.get()
        for number in range(5):
            publish(f"Casa Extra {number}")
        with CaptureQueriesContext(connection) as six:
            self.get()
        self.assertEqual(len(one), len(six))

    def test_no_contact_no_cta_nor_block(self):
        html = self.get()
        self.assertNotIn('id="contacto"', html)
        self.assertNotIn('href="#contacto"', html)
        self.assertNotIn("Conversemos tu proyecto", html)
        self.assertNotIn("¿Tienes un proyecto en mente?", html)

    def test_email_only_shows_mailto(self):
        configure(email="oficina@example.com")
        html = self.get()
        self.assertIn('id="contacto"', html)
        self.assertIn('href="#contacto"', html)
        self.assertIn("¿Tienes un proyecto en mente?", html)
        self.assertIn("Cuéntanos qué quieres construir y conversemos cómo hacerlo realidad.", html)
        contact = re.search(r'<section[^>]*id="contacto".*?</section>', html, re.S).group(0)
        self.assertIn('href="mailto:oficina@example.com"', contact)
        self.assertNotIn("tel:", contact)
        self.assertNotIn("wa.me", contact)

    def test_contact_shows_all_configured_channels(self):
        configure(whatsapp="+56 9 1234 5678", phone="+56 (2) 2345-6789", email="oficina@example.com")
        html = self.get()
        contact = re.search(r'<section[^>]*id="contacto".*?</section>', html, re.S).group(0)
        self.assertIn('href="https://wa.me/56912345678?text=', contact)
        self.assertIn('href="tel:+56223456789"', contact)
        self.assertIn('href="mailto:oficina@example.com"', contact)
        for label in ("WhatsApp", "Teléfono", "Correo"):
            self.assertIn(label, contact)


class TelDigitsTests(SimpleTestCase):
    def test_keeps_plus_and_digits(self):
        self.assertEqual(tel_digits("+56 (2) 2345-6789"), "+56223456789")
        self.assertEqual(tel_digits("22345 6789"), "223456789")
        self.assertEqual(tel_digits(""), "")
