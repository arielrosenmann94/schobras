import io
import tempfile

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from projects import services
from projects.models import Category, Project


def make_image():
    buffer = io.BytesIO()
    Image.new("RGB", (20, 20), "gray").save(buffer, format="JPEG")
    return SimpleUploadedFile("f.jpg", buffer.getvalue(), content_type="image/jpeg")


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class AdminActionTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_superuser("root", "r@example.com", "pw-12345-x")
        self.client.force_login(user)
        category = Category.objects.get(name="Residencial")
        kwargs = dict(
            category=category,
            intervention_type="remodel",
            commune="Colina",
            region="metropolitana",
        )
        self.empty = Project.objects.create(title="Sin fotos", **kwargs)
        self.full = Project.objects.create(title="Con fotos", **kwargs)
        services.add_photos(self.full, [make_image()])

    def test_publish_action_reports_error_without_crashing(self):
        url = reverse("admin:projects_project_changelist")
        response = self.client.post(
            url,
            {
                "action": "publish_selected",
                "_selected_action": [str(self.empty.pk), str(self.full.pk)],
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        texts = [str(m) for m in get_messages(response.wsgi_request)]
        self.assertTrue(any("Agrega al menos una foto" in t for t in texts))
        self.empty.refresh_from_db()
        self.full.refresh_from_db()
        self.assertEqual(self.empty.status, Project.Status.DRAFT)
        self.assertEqual(self.full.status, Project.Status.PUBLISHED)
