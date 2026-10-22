import io
import shutil
import struct
import tempfile
import zlib
from unittest import mock

from PIL import Image, ImageFile
from cloudinary.exceptions import Error as CloudinaryError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import User
from projects import services
from projects.models import Category, Project, ProjectPhoto



def make_png_bytes():
    buffer = io.BytesIO()
    Image.new("RGB", (4, 4), "white").save(buffer, format="PNG")
    return buffer.getvalue()


PNG = make_png_bytes()
GIF = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
FORMAT_ERROR = "Formato no soportado: sube fotos JPG, PNG o WebP."
UPLOAD_ERROR = "No se pudo subir la foto. Inténtalo de nuevo en unos minutos."


def png(name):
    return SimpleUploadedFile(name, PNG, "image/png")


def png_chunk(kind, data):
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))


def png_with_chunk(kind, data):
    """PNG válido de 64x64 con un chunk extra justo después de IHDR (byte 33)."""
    buffer = io.BytesIO()
    Image.new("RGB", (64, 64), "green").save(buffer, format="PNG")
    base = buffer.getvalue()
    return base[:33] + png_chunk(kind, data) + base[33:]


def png_header_only(width, height):
    """PNG que declara width x height en la cabecera, sin los píxeles."""
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", ihdr)
        + png_chunk(b"IDAT", zlib.compress(b""))
        + png_chunk(b"IEND", b"")
    )


def truncated_jpeg():
    buffer = io.BytesIO()
    Image.effect_noise((256, 256), 64).convert("RGB").save(buffer, format="JPEG")
    data = buffer.getvalue()
    return data[: len(data) // 2]


class PanelPhotoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.editor = User.objects.create_user(username="claudia", password="x-clave-123")
        cls.category = Category.objects.create(name="Casas")

    def setUp(self):
        media = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, media, ignore_errors=True)
        override = override_settings(MEDIA_ROOT=media)
        override.enable()
        self.addCleanup(override.disable)
        self.client.force_login(self.editor)
        self.project = Project.objects.create(
            title="Casa Lo Barnechea",
            category=self.category,
            intervention_type=Project.InterventionType.NEW_BUILD,
            commune="Lo Barnechea",
            region=Project.Region.METROPOLITANA,
        )
        self.url = reverse("panel:project_photos", args=[self.project.pk])

    def upload(self, *files):
        return self.client.post(self.url, {"images": list(files)})

    def make_photos(self, count):
        from projects import services

        return services.add_photos(self.project, [png(f"f{i}.png") for i in range(count)])

    def test_upload_multiple(self):
        response = self.upload(png("a.png"), png("b.png"), png("c.png"))
        self.assertRedirects(response, self.url)
        photos = list(self.project.photos.order_by("order"))
        self.assertEqual(len(photos), 3)
        self.assertEqual([p.is_cover for p in photos], [True, False, False])

    def test_upload_without_files_shows_message(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Elige al menos una foto.")

    def test_reject_over_15mb(self):
        big = SimpleUploadedFile("grande.jpg", b"x" * (15 * 1024 * 1024 + 1), "image/jpeg")
        response = self.upload(png("a.png"), big)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "La foto grande.jpg pesa más de 15 MB.")
        self.assertEqual(self.project.photos.count(), 0)

    def test_reject_unsupported_format(self):
        for name, content in [("a.gif", GIF), ("nota.jpg", b"esto es texto")]:
            with self.subTest(name=name):
                response = self.upload(png("ok.png"), SimpleUploadedFile(name, content))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, FORMAT_ERROR)
                self.assertEqual(self.project.photos.count(), 0)

    def test_reject_image_bomb(self):
        # Con un límite diminuto, un PNG de 4x4 cuenta como bomba de descompresión.
        with mock.patch.object(Image, "MAX_IMAGE_PIXELS", 1):
            response = self.upload(png("bomba.png"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, FORMAT_ERROR)
        self.assertEqual(self.project.photos.count(), 0)

    def test_reject_truncated_image(self):
        broken = SimpleUploadedFile("corta.png", PNG[: len(PNG) // 2], "image/png")
        response = self.upload(broken)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, FORMAT_ERROR)

    def test_reject_images_that_fail_to_decode(self):
        # QA-1.3: estos archivos daban 500 o "Inténtalo de nuevo en unos minutos".
        cases = {
            # zTXt que descomprime a 2 MB en 2 KB de disco: ValueError al abrir.
            "texto.png": png_with_chunk(b"zTXt", b"k\x00\x00" + zlib.compress(b"A" * 2_000_000)),
            # eXIf que no es TIFF: SyntaxError al orientar la foto.
            "exif.png": png_with_chunk(b"eXIf", b"garbage-not-tiff"),
            # JPEG cortado a la mitad: pasa verify() y falla al decodificar.
            "cortada.jpg": truncated_jpeg(),
        }
        for name, content in cases.items():
            with self.subTest(name=name):
                response = self.upload(SimpleUploadedFile(name, content, "image/png"))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, FORMAT_ERROR)
                self.assertNotContains(response, UPLOAD_ERROR)
                self.assertEqual(self.project.photos.count(), 0)

    def test_reject_over_40_megapixels(self):
        # K1: 8000 x 6000 = 48 MP; se rechaza leyendo solo la cabecera.
        huge = SimpleUploadedFile("enorme.png", png_header_only(8000, 6000), "image/png")
        real_load = ImageFile.ImageFile.load

        def load_unless_huge(image):
            if image.size == (8000, 6000):
                raise AssertionError("decodificó la foto de 48 MP")
            return real_load(image)

        with mock.patch.object(ImageFile.ImageFile, "load", load_unless_huge):
            response = self.upload(png("ok.png"), huge)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "La foto enorme.png tiene demasiados megapíxeles (máximo 40)."
        )
        self.assertEqual(self.project.photos.count(), 0)

    def test_reencode_failure_shows_format_error(self):
        # Defensa en profundidad: si algo pasa el formulario y falla al re-codificar.
        with mock.patch(
            "panel.views.PhotoUploadForm.clean_images",
            lambda form: form.cleaned_data["images"],
        ):
            response = self.upload(SimpleUploadedFile("cortada.jpg", truncated_jpeg(), "image/jpeg"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, FORMAT_ERROR)
        self.assertNotContains(response, UPLOAD_ERROR)
        self.assertEqual(ProjectPhoto.objects.count(), 0)

    def test_upload_requires_login(self):
        self.client.logout()
        self.assertEqual(self.upload(png("a.png")).status_code, 302)
        self.assertEqual(self.project.photos.count(), 0)

    def test_list_shows_photos_and_cover_badge(self):
        self.make_photos(2)
        response = self.client.get(self.url)
        self.assertContains(response, "Portada", count=1)
        self.assertContains(response, "<img", count=2)

    def test_move_up_down(self):
        first, second = self.make_photos(2)
        self.client.post(reverse("panel:photo_up", args=[second.pk]))
        second.refresh_from_db()
        first.refresh_from_db()
        self.assertLess(second.order, first.order)
        response = self.client.post(reverse("panel:photo_down", args=[second.pk]))
        self.assertRedirects(response, self.url)
        second.refresh_from_db()
        first.refresh_from_db()
        self.assertLess(first.order, second.order)

    def test_set_cover(self):
        first, second = self.make_photos(2)
        response = self.client.post(reverse("panel:photo_cover", args=[second.pk]))
        self.assertRedirects(response, self.url)
        first.refresh_from_db()
        second.refresh_from_db()
        self.assertFalse(first.is_cover)
        self.assertTrue(second.is_cover)

    def test_delete_last_photo_hides_project(self):
        (photo,) = self.make_photos(1)
        self.project.status = Project.Status.PUBLISHED
        self.project.save()
        self.assertEqual(Project.objects.published().count(), 1)
        response = self.client.post(reverse("panel:photo_delete", args=[photo.pk]))
        self.assertRedirects(response, self.url)
        self.assertEqual(ProjectPhoto.objects.count(), 0)
        self.assertEqual(Project.objects.published().count(), 0)

    def test_delete_cover_promotes_another(self):
        first, second = self.make_photos(2)
        self.client.post(reverse("panel:photo_delete", args=[first.pk]))
        second.refresh_from_db()
        self.assertTrue(second.is_cover)

    def test_actions_are_post_only(self):
        (photo,) = self.make_photos(1)
        for name in ["photo_up", "photo_down", "photo_cover", "photo_delete"]:
            with self.subTest(name=name):
                response = self.client.get(reverse(f"panel:{name}", args=[photo.pk]))
                self.assertEqual(response.status_code, 405)

    def test_delete_has_confirmation_step(self):
        self.make_photos(1)
        response = self.client.get(self.url)
        self.assertContains(response, "Sí, eliminar esta foto")

    def test_permission_notice_visible(self):
        response = self.client.get(self.url)
        self.assertContains(
            response,
            "Sube solo fotos de obras que el dueño autorizó a publicar. "
            "No incluyas números de casa ni patentes.",
        )
        self.assertContains(response, 'accept="image/jpeg,image/png,image/webp"')
        self.assertContains(response, "multiple")

    def test_storage_failure_shows_message_without_500(self):
        for error in (OSError("disco lleno"), CloudinaryError("timeout de Cloudinary")):
            with self.subTest(error=type(error).__name__):
                with (
                    mock.patch(
                        "django.core.files.storage.FileSystemStorage._save", side_effect=error
                    ),
                    self.assertLogs("panel.views", level="ERROR") as logs,
                ):
                    response = self.upload(png("a.png"))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, UPLOAD_ERROR)
                self.assertNotContains(response, str(error))
                self.assertEqual(ProjectPhoto.objects.count(), 0)
                self.assertIn("Traceback", logs.output[0])

    def test_delete_photo_removes_file(self):
        (photo,) = self.make_photos(1)
        storage, name = photo.image.storage, photo.image.name
        with self.captureOnCommitCallbacks(execute=True):
            self.client.post(reverse("panel:photo_delete", args=[photo.pk]))
        self.assertFalse(storage.exists(name))

    def test_delete_project_removes_files(self):
        photos = self.make_photos(2)
        storage = photos[0].image.storage
        names = [photo.image.name for photo in photos]
        with (
            mock.patch("panel.views.services.delete_project", wraps=services.delete_project) as spy,
            self.captureOnCommitCallbacks(execute=True),
        ):
            response = self.client.post(reverse("panel:project_delete", args=[self.project.pk]))
        self.assertRedirects(response, reverse("panel:home"))
        spy.assert_called_once()
        self.assertFalse(Project.objects.filter(pk=self.project.pk).exists())
        for name in names:
            self.assertFalse(storage.exists(name))

    def test_thumbnails_use_400px_variant_and_stored_size(self):
        self.make_photos(1)
        cloudinary_url = "https://res.cloudinary.com/demo/image/upload/v1/proyectos/f0.jpg"
        with mock.patch(
            "django.core.files.storage.FileSystemStorage.url", return_value=cloudinary_url
        ):
            response = self.client.get(self.url)
        self.assertContains(
            response,
            'src="https://res.cloudinary.com/demo/image/upload/f_auto,q_auto,c_limit,w_400/v1/proyectos/f0.jpg"',
        )
        self.assertRegex(
            response.content.decode(),
            r'<img src="[^"]+w_400[^"]+" alt="[^"]+" width="4" height="4" loading="lazy">',
        )

    def test_upload_help_text_linked_to_input(self):
        html = self.client.get(self.url).content.decode()
        self.assertIn(
            '<p class="help" id="id_images_helptext">'
            "Puedes subir varias a la vez; si tu conexión es lenta, sube de a 5.</p>",
            html,
        )
        self.assertRegex(html, r'<input type="file"[^>]*aria-describedby="id_images_helptext"')
