import contextlib
import io
import tempfile
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import ExifTags, Image, ImageFile

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


def make_photo_bytes(size, image_format="JPEG", mode="RGB", color="gray", **save_kwargs):
    buffer = io.BytesIO()
    Image.new(mode, size, color).save(buffer, format=image_format, **save_kwargs)
    return buffer.getvalue()


def phone_exif():
    """EXIF de celular: foto girada (orientación 6) y con coordenadas GPS."""
    exif = Image.Exif()
    exif[ExifTags.Base.Orientation] = 6
    gps = exif.get_ifd(ExifTags.IFD.GPSInfo)
    gps[ExifTags.GPS.GPSLatitudeRef] = "S"
    gps[ExifTags.GPS.GPSLatitude] = (33.0, 26.0, 0.0)
    return exif


@contextlib.contextmanager
def record_full_size_copies():
    """Anota cada copia de una foto de más de MAX_SIDE px (convert, copy, transpose).

    QA-2.1 (K1): con 40 MP cada copia a tamaño completo son 160 MB; la foto
    se reduce primero y recién después se orienta y se convierte.
    """
    copies = []

    def spy(name, real):
        def wrapper(image, *args, **kwargs):
            if max(image.size) > services.MAX_SIDE:
                copies.append((name, image.size))
            return real(image, *args, **kwargs)

        return wrapper

    with contextlib.ExitStack() as stack:
        for name in ("convert", "copy", "transpose"):
            real = getattr(Image.Image, name)
            stack.enter_context(mock.patch.object(Image.Image, name, spy(name, real)))
        yield copies


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class AddPhotosReencodeTests(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            title="Casa Pirque",
            category=Category.objects.get(name="Residencial"),
            intervention_type=Project.InterventionType.NEW_BUILD,
            commune="Pirque",
            region=Project.Region.METROPOLITANA,
        )

    def add(self, name, content, content_type="image/jpeg"):
        (photo,) = services.add_photos(
            self.project, [SimpleUploadedFile(name, content, content_type=content_type)]
        )
        return photo

    def test_rotates_by_exif_and_strips_metadata(self):
        photo = self.add("IMG_0001.JPG", make_photo_bytes((40, 20), exif=phone_exif()))
        with Image.open(photo.image.path) as stored:
            self.assertEqual(stored.size, (20, 40))
            self.assertEqual(stored.format, "JPEG")
            exif = stored.getexif()
            self.assertEqual(len(exif), 0)
            self.assertEqual(exif.get_ifd(ExifTags.IFD.GPSInfo), {})
        self.assertEqual((photo.image_width, photo.image_height), (20, 40))

    def test_strips_jpeg_comment(self):
        # QA-1.8: el comentario COM del JPEG sobrevivía al re-encode.
        buffer = io.BytesIO()
        Image.new("RGB", (30, 30), "gray").save(
            buffer, format="JPEG", comment=b"COMMENT-PERSONAL-DATA"
        )
        photo = self.add("gps.jpg", buffer.getvalue())
        with open(photo.image.path, "rb") as stored_file:
            found = b"COMMENT-PERSONAL-DATA" in stored_file.read()
        self.assertFalse(found, "el comentario JPEG quedó en la foto guardada")
        with Image.open(photo.image.path) as stored:
            self.assertNotIn("comment", stored.info)

    def test_large_photo_is_reduced_to_2560(self):
        photo = self.add("grande.jpg", make_photo_bytes((4000, 3000)))
        with Image.open(photo.image.path) as stored:
            self.assertEqual(stored.size, (2560, 1920))
        self.assertEqual((photo.image_width, photo.image_height), (2560, 1920))

    def test_large_photo_is_never_copied_at_full_size(self):
        # QA-2.1 (K1): exif_transpose y convert copiaban la foto completa (505 MB con 40 MP).
        cases = {
            "girada.jpg": (make_photo_bytes((3000, 2000), exif=phone_exif()), (1707, 2560)),
            "plano.png": (make_photo_bytes((3000, 2000), "PNG"), (2560, 1707)),
            "render.webp": (make_photo_bytes((3000, 2000), "WEBP"), (2560, 1707)),
        }
        # Con transparencia, Pillow copia la foto al reducirla (premultiplica el
        # alfa); por eso PNG y WebP tienen un tope de megapíxeles menor.
        for name, (content, size) in cases.items():
            with self.subTest(name=name):
                with record_full_size_copies() as copies:
                    photo = self.add(name, content)
                self.assertEqual(copies, [])
                self.assertEqual((photo.image_width, photo.image_height), size)

    def test_large_palette_png_is_smoothed_when_reduced(self):
        # Pillow reduce las imágenes de paleta sin suavizar; se pasan a color antes.
        stripes = Image.new("L", (3000, 2000), 0)
        for x in range(0, 3000, 2):
            stripes.paste(255, (x, 0, x + 1, 2000))
        palette = stripes.convert("P")
        buffer = io.BytesIO()
        palette.save(buffer, format="PNG", transparency=0)
        photo = self.add("plano.png", buffer.getvalue(), "image/png")
        with Image.open(photo.image.path) as stored:
            self.assertEqual(stored.size, (2560, 1707))
            self.assertGreater(len(stored.getcolors(2560 * 1707)), 2)

    def test_large_jpeg_is_decoded_at_reduced_scale(self):
        # QA-2.1 (K1): un JPEG de 5200 x 3000 se decodifica a la mitad (2600 x 1500),
        # que todavía alcanza para los 2560 px finales.
        loaded = set()
        real_load = ImageFile.ImageFile.load

        def spy_load(image):
            loaded.add(image.size)
            return real_load(image)

        with mock.patch.object(ImageFile.ImageFile, "load", spy_load):
            photo = self.add("grande.jpg", make_photo_bytes((5200, 3000)))
        self.assertIn((2600, 1500), loaded)
        self.assertNotIn((5200, 3000), loaded)
        self.assertEqual((photo.image_width, photo.image_height), (2560, 1477))

    def test_transparent_png_stays_png(self):
        content = make_photo_bytes((30, 30), "PNG", mode="RGBA", color=(0, 0, 0, 0))
        photo = self.add("logo.png", content, "image/png")
        self.assertTrue(photo.image.name.endswith(".png"))
        with Image.open(photo.image.path) as stored:
            self.assertEqual(stored.format, "PNG")
            self.assertIn("A", stored.getbands())

    def test_opaque_png_and_webp_become_jpeg(self):
        for name, image_format in [("plano.png", "PNG"), ("render.webp", "WEBP")]:
            with self.subTest(name=name):
                photo = self.add(name, make_photo_bytes((30, 30), image_format))
                self.assertTrue(photo.image.name.endswith(".jpg"))
                with Image.open(photo.image.path) as stored:
                    self.assertEqual(stored.format, "JPEG")

    def test_file_name_is_sanitized_with_right_extension(self):
        photo = self.add("Fachada Ñuñoa (1).JPEG", make_photo_bytes((30, 30)))
        base = photo.image.name.rsplit("/", 1)[-1]
        self.assertRegex(base, r"^fachada-nunoa-1(_\w+)?\.jpg$")

    def test_transparent_png_too_heavy_falls_back_to_jpeg(self):
        content = make_photo_bytes((30, 30), "PNG", mode="RGBA", color=(0, 0, 0, 0))
        with mock.patch.object(services, "MAX_STORED_BYTES", 10):
            photo = self.add("logo.png", content, "image/png")
        self.assertTrue(photo.image.name.endswith(".jpg"))


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class DeleteFilesTests(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            title="Casa Buin",
            category=Category.objects.get(name="Residencial"),
            intervention_type=Project.InterventionType.NEW_BUILD,
            commune="Buin",
            region=Project.Region.METROPOLITANA,
        )

    def test_delete_photo_removes_file_after_commit(self):
        (photo,) = services.add_photos(self.project, [make_image()])
        storage, name = photo.image.storage, photo.image.name
        self.assertTrue(storage.exists(name))
        with self.captureOnCommitCallbacks(execute=True):
            services.delete_photo(photo)
        self.assertFalse(storage.exists(name))

    def test_delete_project_removes_project_photos_and_files(self):
        photos = services.add_photos(self.project, [make_image("a.jpg"), make_image("b.jpg")])
        storage = photos[0].image.storage
        names = [photo.image.name for photo in photos]
        with self.captureOnCommitCallbacks(execute=True):
            services.delete_project(self.project)
        self.assertFalse(Project.objects.filter(pk=self.project.pk).exists())
        self.assertFalse(ProjectPhoto.objects.exists())
        for name in names:
            self.assertFalse(storage.exists(name))
