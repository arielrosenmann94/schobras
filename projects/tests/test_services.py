import io
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image

from projects import services
from projects.models import Category, Project, ProjectPhoto


def make_image(name="foto.jpg"):
    buffer = io.BytesIO()
    Image.new("RGB", (20, 20), "gray").save(buffer, format="JPEG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/jpeg")


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ServiceTests(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            title="Casa Chicureo",
            category=Category.objects.get(name="Residencial"),
            intervention_type=Project.InterventionType.REMODEL,
            commune="Colina",
            region=Project.Region.METROPOLITANA,
        )

    def test_publish_without_photos_raises(self):
        with self.assertRaisesMessage(
            services.PublishError, "Agrega al menos una foto antes de publicar."
        ):
            services.publish(self.project)
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, Project.Status.DRAFT)

    def test_publish_with_photo(self):
        services.add_photos(self.project, [make_image()])
        services.publish(self.project)
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, Project.Status.PUBLISHED)
        self.assertIn(self.project, Project.objects.published())
        services.unpublish(self.project)
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, Project.Status.DRAFT)

    def test_add_photos_order_and_first_cover(self):
        photos = services.add_photos(self.project, [make_image("a.jpg"), make_image("b.jpg")])
        self.assertEqual([p.order for p in photos], [1, 2])
        self.assertEqual([p.is_cover for p in photos], [True, False])
        more = services.add_photos(self.project, [make_image("c.jpg")])
        self.assertEqual(more[0].order, 3)
        self.assertFalse(more[0].is_cover)

    def test_set_cover_unsets_others(self):
        first, second = services.add_photos(self.project, [make_image(), make_image()])
        services.set_cover(second)
        first.refresh_from_db()
        second.refresh_from_db()
        self.assertFalse(first.is_cover)
        self.assertTrue(second.is_cover)
        self.assertEqual(self.project.photos.filter(is_cover=True).count(), 1)

    def test_move_photo_up_down_swaps_order(self):
        a, b, c = services.add_photos(self.project, [make_image() for _ in range(3)])
        services.move_photo(b, "up")
        self.assertEqual(list(self.project.photos.all()), [b, a, c])
        services.move_photo(b, "up")
        self.assertEqual(list(self.project.photos.all()), [b, a, c])
        services.move_photo(c, "down")
        self.assertEqual(list(self.project.photos.all()), [b, a, c])
        services.move_photo(b, "down")
        self.assertEqual(list(self.project.photos.all()), [a, b, c])

    def test_delete_last_photo_hides_project(self):
        (photo,) = services.add_photos(self.project, [make_image()])
        services.publish(self.project)
        services.delete_photo(photo)
        self.assertFalse(ProjectPhoto.objects.filter(project=self.project).exists())
        self.assertNotIn(self.project, Project.objects.published())
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, Project.Status.PUBLISHED)
