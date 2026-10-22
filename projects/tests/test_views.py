import re
import tempfile
from unittest import mock

from django.test import TestCase, override_settings
from django.urls import reverse

from core.models import SiteSettings
from projects.models import Category, Project, ProjectPhoto

from .test_models import make_image, make_project


def configure_whatsapp():
    settings_obj = SiteSettings.load()
    settings_obj.whatsapp = "912345678"
    settings_obj.save()


def publish(title="Casa Chicureo", **extra):
    project = make_project(title, **extra)
    ProjectPhoto.objects.create(project=project, image=make_image(), order=1, is_cover=True)
    project.status = Project.Status.PUBLISHED
    project.save()
    return project


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ProjectListTests(TestCase):
    def test_list_empty_message(self):
        response = self.client.get(reverse("projects:list"))
        self.assertContains(response, "Pronto publicaremos nuestras obras")

    def test_list_only_published(self):
        publish("Casa Publicada")
        make_project("Casa Borrador")
        draft_with_photo = make_project("Borrador con foto")
        ProjectPhoto.objects.create(project=draft_with_photo, image=make_image(), order=1)
        published_no_photo = make_project("Publicada sin fotos")
        Project.objects.filter(pk=published_no_photo.pk).update(status=Project.Status.PUBLISHED)
        response = self.client.get(reverse("projects:list"))
        self.assertContains(response, "Casa Publicada")
        self.assertNotContains(response, "Casa Borrador")
        self.assertNotContains(response, "Borrador con foto")
        self.assertNotContains(response, "Publicada sin fotos")

    def test_list_title(self):
        publish()
        response = self.client.get(reverse("projects:list"))
        self.assertContains(response, "<title>Proyectos | SCHOBRAS.CL</title>", html=True)

    def test_first_card_image_is_lcp_priority(self):
        for title in ("Casa Uno", "Casa Dos", "Casa Tres"):
            publish(title)
        html = self.client.get(reverse("projects:list")).content.decode()
        grid = html.split('class="projects__grid"', 1)[1]
        images = re.findall(r"<img [^>]*>", grid)
        self.assertEqual(len(images), 3)
        self.assertIn('fetchpriority="high"', images[0])
        self.assertNotIn('loading="lazy"', images[0])
        for image in images[1:]:
            self.assertIn('loading="lazy"', image)
            self.assertNotIn("fetchpriority", image)

    def test_category_filter(self):
        residential = Category.objects.get(name="Residencial")
        other = Category.objects.exclude(pk=residential.pk).first()
        publish("Casa Uno", category=residential)
        publish("Otra Obra", category=other)
        response = self.client.get(reverse("projects:category", args=[residential.slug]))
        self.assertContains(response, "Casa Uno")
        self.assertNotContains(response, "Otra Obra")
        self.assertContains(response, "Todos")

    def test_unknown_category_404(self):
        response = self.client.get("/proyectos/categoria/no-existe/")
        self.assertEqual(response.status_code, 404)

    def test_category_route_wins_over_detail_slug(self):
        self.assertEqual(reverse("projects:category", args=["x"]), "/proyectos/categoria/x/")

    def test_inactive_category_hidden_from_filters_projects_still_listed(self):
        inactive = Category.objects.get(name="Residencial")
        publish("Casa Oculta", category=inactive)
        Category.objects.filter(pk=inactive.pk).update(is_active=False)
        response = self.client.get(reverse("projects:list"))
        self.assertContains(response, "Casa Oculta")
        self.assertNotContains(response, reverse("projects:category", args=[inactive.slug]))
        self.assertEqual(
            self.client.get(reverse("projects:category", args=[inactive.slug])).status_code, 404
        )

    def test_filters_only_categories_with_published_projects(self):
        publish("Casa Uno")
        empty = Category.objects.exclude(name="Residencial").first()
        response = self.client.get(reverse("projects:list"))
        self.assertNotContains(response, reverse("projects:category", args=[empty.slug]))

    def test_list_images_have_dimensions(self):
        publish()
        html = self.client.get(reverse("projects:list")).content.decode()
        self.assertRegex(html, r'<img[^>]*width="20"[^>]*height="20"')


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ProjectDetailTests(TestCase):
    def test_detail_shows_only_filled_fields(self):
        project = publish(area_m2=120)
        html = self.client.get(project.get_absolute_url()).content.decode()
        self.assertIn("120", html)
        self.assertIn("Colina", html)
        self.assertIn("Región Metropolitana", html)
        self.assertNotIn("Año", html)
        self.assertNotIn("Sistemas constructivos", html)
        project.year = 2024
        project.construction_systems = ["timber"]
        project.save()
        html = self.client.get(project.get_absolute_url()).content.decode()
        self.assertIn("2024", html)
        self.assertIn("Madera", html)

    def test_detail_title_and_cta(self):
        configure_whatsapp()
        project = publish()
        response = self.client.get(project.get_absolute_url())
        self.assertContains(response, "Casa Chicureo en Colina | SCHOBRAS.CL")
        self.assertContains(response, "¿Tienes un proyecto parecido? Conversemos.")

    def test_detail_cover_high_priority_and_gallery_link(self):
        project = publish()
        ProjectPhoto.objects.create(project=project, image=make_image(), order=2)
        html = self.client.get(project.get_absolute_url()).content.decode()
        self.assertIn('fetchpriority="high"', html)
        self.assertIn("data-gallery", html)

    def test_detail_draft_404(self):
        project = make_project("Borrador")
        ProjectPhoto.objects.create(project=project, image=make_image(), order=1)
        self.assertEqual(self.client.get(project.get_absolute_url()).status_code, 404)

    def test_detail_no_contact_no_cta(self):
        project = publish()
        self.assertNotContains(self.client.get(project.get_absolute_url()), "Conversemos")

    def test_detail_without_photos_404(self):
        project = make_project("Sin fotos")
        Project.objects.filter(pk=project.pk).update(status=Project.Status.PUBLISHED)
        self.assertEqual(self.client.get(project.get_absolute_url()).status_code, 404)

    def test_detail_whatsapp_mentions_project(self):
        configure_whatsapp()
        project = publish("Casa O'Higgins")
        html = self.client.get(project.get_absolute_url()).content.decode()
        self.assertIn("text=Hola%2C%20vi%20el%20proyecto%20Casa%20O%27Higgins%20y%20quiero", html)

    def test_photo_saves_dimensions(self):
        project = publish()
        photo = project.photos.get()
        self.assertEqual((photo.image_width, photo.image_height), (20, 20))

    def test_render_does_not_open_files(self):
        project = publish()
        ProjectPhoto.objects.create(project=project, image=make_image(), order=2)
        with mock.patch(
            "django.core.files.storage.FileSystemStorage._open", side_effect=OSError("no abrir")
        ):
            for url in (project.get_absolute_url(), reverse("projects:list")):
                html = self.client.get(url).content.decode()
                self.assertRegex(html, r'<img[^>]*width="20"[^>]*height="20"')
