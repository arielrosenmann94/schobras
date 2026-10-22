import io
import tempfile

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import ProtectedError
from django.test import TestCase, override_settings
from PIL import Image
from uuid6 import UUID

from projects.models import Category, Project, ProjectPhoto


def make_image(name="foto.jpg"):
    buffer = io.BytesIO()
    Image.new("RGB", (20, 20), "gray").save(buffer, format="JPEG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/jpeg")


def make_project(title="Casa Chicureo", category=None, **extra):
    category = category or Category.objects.get(name="Residencial")
    return Project.objects.create(
        title=title,
        category=category,
        intervention_type=Project.InterventionType.NEW_BUILD,
        commune="Colina",
        region=Project.Region.METROPOLITANA,
        **extra,
    )


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ProjectModelTests(TestCase):
    def test_slug_generated_and_stable_on_edit(self):
        project = make_project()
        self.assertEqual(project.slug, "casa-chicureo")
        project.title = "Otro nombre"
        project.save()
        project.refresh_from_db()
        self.assertEqual(project.slug, "casa-chicureo")

    def test_duplicate_titles_unique_slugs(self):
        first = make_project()
        second = make_project()
        third = make_project()
        self.assertEqual(first.slug, "casa-chicureo")
        self.assertEqual(second.slug, "casa-chicureo-2")
        self.assertEqual(third.slug, "casa-chicureo-3")

    def test_slug_respects_max_length(self):
        long_title = "a" * 150
        first = make_project(title=long_title)
        second = make_project(title=long_title)
        self.assertLessEqual(len(first.slug), 170)
        self.assertLessEqual(len(second.slug), 170)
        self.assertNotEqual(first.slug, second.slug)

    def test_published_excludes_drafts(self):
        project = make_project()
        ProjectPhoto.objects.create(project=project, image=make_image())
        self.assertNotIn(project, Project.objects.published())

    def test_published_excludes_without_photos(self):
        project = make_project(status=Project.Status.PUBLISHED)
        self.assertNotIn(project, Project.objects.published())
        ProjectPhoto.objects.create(project=project, image=make_image(), order=1)
        ProjectPhoto.objects.create(project=project, image=make_image(), order=2)
        self.assertEqual(list(Project.objects.published()), [project])

    def test_cover_photo_flagged_or_first(self):
        project = make_project()
        self.assertIsNone(project.cover_photo)
        second = ProjectPhoto.objects.create(project=project, image=make_image(), order=2)
        first = ProjectPhoto.objects.create(project=project, image=make_image(), order=1)
        self.assertEqual(project.cover_photo, first)
        second.is_cover = True
        second.save()
        self.assertEqual(project.cover_photo, second)

    def test_alt_falls_back_to_title(self):
        project = make_project()
        photo = ProjectPhoto.objects.create(project=project, image=make_image())
        self.assertEqual(photo.alt, "Casa Chicureo")
        photo.alt_text = "Fachada norte"
        self.assertEqual(photo.alt, "Fachada norte")

    def test_delete_category_with_projects_raises(self):
        project = make_project()
        with self.assertRaises(ProtectedError):
            project.category.delete()

    def test_construction_systems_display(self):
        project = make_project(construction_systems=["masonry", "sip_panels"])
        self.assertEqual(project.construction_systems_display, ["Albañilería", "Paneles SIP"])

    def test_clean_rejects_unknown_construction_system(self):
        project = make_project(construction_systems=["magia"])
        with self.assertRaises(ValidationError):
            project.full_clean()

    def test_initial_categories(self):
        names = list(Category.objects.values_list("name", flat=True))
        self.assertEqual(names, ["Residencial", "Comercial", "Industrial"])

    def test_no_address_field(self):
        for field in Project._meta.get_fields():
            self.assertNotIn("address", field.name)
            self.assertNotIn("direccion", field.name)

    def test_pk_is_uuid7(self):
        project = make_project()
        self.assertEqual(UUID(str(project.pk)).version, 7)
