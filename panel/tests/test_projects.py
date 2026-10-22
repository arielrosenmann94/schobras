import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from projects.models import Category, Project, ProjectPhoto

PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06"
    b"\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\xff\xff?\x00\x05\xfe"
    b"\x02\xfe\xa75\x81\x84\x00\x00\x00\x00IEND\xaeB`\x82"
)


class PanelProjectTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.editor = User.objects.create_user(username="claudia", password="x-clave-123")
        cls.category = Category.objects.create(name="Casas")

    def setUp(self):
        self.client.force_login(self.editor)

    def make_project(self, **extra):
        data = {
            "title": "Casa Lo Barnechea",
            "category": self.category,
            "intervention_type": Project.InterventionType.NEW_BUILD,
            "commune": "Lo Barnechea",
            "region": Project.Region.METROPOLITANA,
        }
        data.update(extra)
        return Project.objects.create(**data)

    def add_photo(self, project):
        return ProjectPhoto.objects.create(
            project=project, image=SimpleUploadedFile("a.png", PNG, "image/png"), order=1
        )

    def form_data(self, **extra):
        data = {
            "title": "Casa Nueva",
            "category": self.category.pk,
            "intervention_type": "new_build",
            "commune": "Vitacura",
            "region": "metropolitana",
            "construction_systems": ["timber", "steel"],
            "area_m2": "120",
            "year": "2025",
            "description": "Una casa.",
        }
        data.update(extra)
        return data

    def test_create_project_is_draft_and_redirects_to_photos(self):
        response = self.client.post(reverse("panel:project_create"), self.form_data())
        project = Project.objects.get(title="Casa Nueva")
        self.assertEqual(project.status, Project.Status.DRAFT)
        self.assertEqual(project.construction_systems, ["timber", "steel"])
        self.assertRedirects(
            response, reverse("panel:project_photos", args=[project.pk])
        )

    def test_construction_systems_grouped_in_fieldset(self):
        html = self.client.get(reverse("panel:project_create")).content.decode()
        self.assertRegex(
            html, r'<fieldset class="field">\s*<legend>Sistemas constructivos</legend>'
        )
        self.assertNotIn("<label>Sistemas constructivos</label>", html)

    def test_error_and_success_messages_are_distinct(self):
        project = self.make_project()
        response = self.client.post(
            reverse("panel:project_toggle_publish", args=[project.pk]), follow=True
        )
        self.assertContains(
            response,
            '<p class="message message--error" role="alert">Agrega al menos una foto antes de publicar.</p>',
            html=True,
        )
        response = self.client.post(
            reverse("panel:category_create"), {"name": "Galpones", "order": "1"}, follow=True
        )
        self.assertContains(
            response,
            '<p class="message message--success" role="status">Categoría creada.</p>',
            html=True,
        )

    def test_header_brand_links_home_and_has_favicon(self):
        response = self.client.get(reverse("panel:categories"))
        self.assertRegex(
            response.content.decode(),
            r'<a[^>]*href="%s"[^>]*>SCHOBRAS\.CL <span>Panel</span></a>' % reverse("panel:home"),
        )
        self.assertContains(response, '<link rel="icon" href="/static/img/favicon.svg" type="image/svg+xml">')

    def test_year_out_of_range_shows_spanish_message(self):
        max_year = timezone.localdate().year + 2
        response = self.client.post(reverse("panel:project_create"), self.form_data(year="3000"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"El año debe estar entre 1950 y {max_year}.")
        self.assertFalse(Project.objects.filter(title="Casa Nueva").exists())

    def test_category_active_label(self):
        response = self.client.get(reverse("panel:category_create"))
        self.assertContains(response, "Activa (aparece en la web y al crear proyectos)")

    def test_create_form_lists_only_active_categories(self):
        Category.objects.create(name="Antigua", is_active=False)
        response = self.client.get(reverse("panel:project_create"))
        self.assertContains(response, "Casas")
        self.assertNotContains(response, "Antigua")

    def test_publish_without_photos_shows_message(self):
        project = self.make_project()
        response = self.client.post(
            reverse("panel:project_toggle_publish", args=[project.pk]), follow=True
        )
        self.assertContains(response, "Agrega al menos una foto antes de publicar.")
        project.refresh_from_db()
        self.assertEqual(project.status, Project.Status.DRAFT)

    @override_settings(MEDIA_ROOT="/tmp/schobras-test-media")
    def test_publish_and_unpublish(self):
        project = self.make_project()
        self.add_photo(project)
        url = reverse("panel:project_toggle_publish", args=[project.pk])
        self.client.post(url)
        project.refresh_from_db()
        self.assertEqual(project.status, Project.Status.PUBLISHED)
        edit = self.client.get(reverse("panel:project_edit", args=[project.pk]))
        self.assertContains(edit, f'href="{project.get_absolute_url()}"')
        self.client.post(url)
        project.refresh_from_db()
        self.assertEqual(project.status, Project.Status.DRAFT)
        edit = self.client.get(reverse("panel:project_edit", args=[project.pk]))
        self.assertNotContains(edit, "Ver en la web")

    def toggle_form_html(self, project, label):
        return (
            f'<form method="post" action="{reverse("panel:project_toggle_publish", args=[project.pk])}">'
        ), f'<button type="submit" class="btn btn-secondary">{label}</button>'

    def test_photos_and_edit_pages_have_publish_button(self):
        # QA-1.4: el flujo crear -> fotos -> publicar termina donde está Claudia.
        project = self.make_project()
        form_tag, button = self.toggle_form_html(project, "Publicar")
        for name in ["panel:project_photos", "panel:project_edit"]:
            with self.subTest(page=name):
                html = self.client.get(reverse(name, args=[project.pk])).content.decode()
                self.assertTrue(form_tag in html, f"falta el formulario de publicar en {name}")
                self.assertTrue(button in html, f"falta el botón Publicar en {name}")
        project.status = Project.Status.PUBLISHED
        project.save()
        _, button = self.toggle_form_html(project, "Despublicar")
        for name in ["panel:project_photos", "panel:project_edit"]:
            with self.subTest(page=name, status="published"):
                html = self.client.get(reverse(name, args=[project.pk])).content.decode()
                self.assertTrue(button in html, f"falta el botón Despublicar en {name}")

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_publish_returns_to_the_page_it_came_from(self):
        project = self.make_project()
        self.add_photo(project)
        url = reverse("panel:project_toggle_publish", args=[project.pk])
        cases = [
            ("photos", reverse("panel:project_photos", args=[project.pk])),
            ("edit", reverse("panel:project_edit", args=[project.pk])),
            ("https://malo.example/", reverse("panel:home")),
            ("", reverse("panel:home")),
        ]
        for return_to, expected in cases:
            with self.subTest(return_to=return_to):
                response = self.client.post(url, {"return_to": return_to})
                self.assertRedirects(response, expected, fetch_redirect_response=False)

    def test_publish_from_photos_without_photos_shows_message_there(self):
        project = self.make_project()
        response = self.client.post(
            reverse("panel:project_toggle_publish", args=[project.pk]),
            {"return_to": "photos"},
            follow=True,
        )
        self.assertRedirects(response, reverse("panel:project_photos", args=[project.pk]))
        self.assertContains(response, "Agrega al menos una foto antes de publicar.")
        project.refresh_from_db()
        self.assertEqual(project.status, Project.Status.DRAFT)

    def test_toggle_publish_rejects_get(self):
        project = self.make_project()
        response = self.client.get(
            reverse("panel:project_toggle_publish", args=[project.pk])
        )
        self.assertEqual(response.status_code, 405)

    def test_edit_keeps_slug(self):
        project = self.make_project()
        slug = project.slug
        self.client.post(
            reverse("panel:project_edit", args=[project.pk]),
            self.form_data(title="Otro título"),
        )
        project.refresh_from_db()
        self.assertEqual(project.title, "Otro título")
        self.assertEqual(project.slug, slug)

    def test_delete_requires_post_confirmation(self):
        project = self.make_project()
        url = reverse("panel:project_delete", args=[project.pk])
        response = self.client.get(url)
        self.assertContains(response, "Casa Lo Barnechea")
        self.assertTrue(Project.objects.filter(pk=project.pk).exists())
        response = self.client.post(url)
        self.assertRedirects(response, reverse("panel:home"))
        self.assertFalse(Project.objects.filter(pk=project.pk).exists())

    def test_unknown_pk_is_404(self):
        url = reverse(
            "panel:project_edit", args=["01990000-0000-7000-8000-000000000000"]
        )
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_delete_category_with_projects_message(self):
        self.make_project()
        response = self.client.post(
            reverse("panel:category_delete", args=[self.category.pk]), follow=True
        )
        self.assertContains(
            response,
            "Esta categoría tiene proyectos. Puedes desactivarla en vez de eliminarla.",
        )
        self.assertTrue(Category.objects.filter(pk=self.category.pk).exists())

    def test_delete_empty_category(self):
        empty = Category.objects.create(name="Vacía")
        response = self.client.post(reverse("panel:category_delete", args=[empty.pk]))
        self.assertRedirects(response, reverse("panel:categories"))
        self.assertFalse(Category.objects.filter(pk=empty.pk).exists())

    def test_editor_creates_category(self):
        response = self.client.post(
            reverse("panel:category_create"),
            {"name": "Ampliaciones", "order": "2", "is_active": "on"},
        )
        self.assertRedirects(response, reverse("panel:categories"))
        category = Category.objects.get(name="Ampliaciones")
        self.assertEqual(category.slug, "ampliaciones")

    def test_duplicate_category_name_any_case_rejected(self):
        # QA-1.11: "residencial" con "Residencial" creaba residencial-2.
        for name in ["residencial", "CASAS", "Casas"]:
            with self.subTest(name=name):
                response = self.client.post(
                    reverse("panel:category_create"), {"name": name, "is_active": "on"}
                )
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "Ya existe una categoría con ese nombre.")
        self.assertEqual(Category.objects.filter(name__iexact="residencial").count(), 1)
        self.assertEqual(Category.objects.filter(name__iexact="casas").count(), 1)

    def test_edit_category_case_of_own_name_allowed_but_not_other(self):
        url = reverse("panel:category_edit", args=[self.category.pk])
        response = self.client.post(url, {"name": "CASAS", "is_active": "on"})
        self.assertRedirects(response, reverse("panel:categories"))
        response = self.client.post(url, {"name": "comercial", "is_active": "on"})
        self.assertContains(response, "Ya existe una categoría con ese nombre.")
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "CASAS")

    def test_editor_edits_category(self):
        self.client.post(
            reverse("panel:category_edit", args=[self.category.pk]),
            {"name": "Casas nuevas", "order": "1"},
        )
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Casas nuevas")
        self.assertFalse(self.category.is_active)

    def test_photos_page_shows_notice(self):
        project = self.make_project()
        response = self.client.get(reverse("panel:project_photos", args=[project.pk]))
        self.assertContains(
            response,
            "Sube solo fotos de obras que el dueño autorizó a publicar. "
            "No incluyas números de casa ni patentes.",
        )

    def test_anonymous_is_redirected(self):
        self.client.logout()
        response = self.client.get(reverse("panel:categories"))
        self.assertEqual(response.status_code, 302)


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class PanelPublicStateTests(TestCase):
    """Publicado sin fotos no se ve en la web: el panel lo dice y no ofrece "Ver en la web"."""

    NO_PHOTOS_BADGE = "Publicado · sin fotos, no se ve en la web"

    @classmethod
    def setUpTestData(cls):
        cls.editor = User.objects.create_user(username="claudia", password="x-clave-123")
        cls.category = Category.objects.create(name="Casas")

    def setUp(self):
        self.client.force_login(self.editor)

    def make_project(self, title, published, with_photo):
        project = Project.objects.create(
            title=title,
            category=self.category,
            intervention_type=Project.InterventionType.NEW_BUILD,
            commune="Vitacura",
            region=Project.Region.METROPOLITANA,
            status=Project.Status.PUBLISHED if published else Project.Status.DRAFT,
        )
        if with_photo:
            ProjectPhoto.objects.create(
                project=project, image=SimpleUploadedFile("a.png", PNG, "image/png"), order=1
            )
        return project

    def test_published_without_photos(self):
        project = self.make_project("Casa Sin Fotos", published=True, with_photo=False)
        home = self.client.get(reverse("panel:home"))
        self.assertContains(home, self.NO_PHOTOS_BADGE)
        self.assertNotContains(home, "Ver en la web")
        self.assertNotContains(home, project.get_absolute_url())
        edit = self.client.get(reverse("panel:project_edit", args=[project.pk]))
        self.assertNotContains(edit, "Ver en la web")

    def test_published_with_photo_links_to_web(self):
        project = self.make_project("Casa Con Fotos", published=True, with_photo=True)
        home = self.client.get(reverse("panel:home"))
        self.assertNotContains(home, self.NO_PHOTOS_BADGE)
        self.assertContains(home, "Publicado")
        self.assertContains(home, f'href="{project.get_absolute_url()}"')
        self.assertContains(home, "Ver en la web")
        edit = self.client.get(reverse("panel:project_edit", args=[project.pk]))
        self.assertContains(edit, f'href="{project.get_absolute_url()}"')

    def test_draft_with_photo_has_no_web_link(self):
        project = self.make_project("Casa Borrador", published=False, with_photo=True)
        home = self.client.get(reverse("panel:home"))
        self.assertContains(home, "Borrador")
        self.assertNotContains(home, "Ver en la web")
        edit = self.client.get(reverse("panel:project_edit", args=[project.pk]))
        self.assertNotContains(edit, "Ver en la web")
