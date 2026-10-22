from django.test import SimpleTestCase

from core.templatetags.image_tags import srcset, variant

CLOUD = "https://res.cloudinary.com/x/image/upload/v1/a.jpg"


class ImageTagTests(SimpleTestCase):
    def test_variant_cloudinary(self):
        self.assertEqual(
            variant(CLOUD, 800),
            "https://res.cloudinary.com/x/image/upload/f_auto,q_auto,c_limit,w_800/v1/a.jpg",
        )

    def test_variant_non_matching_unchanged(self):
        for url in (
            "https://res.cloudinary.com/x/raw/upload/v1/a.pdf",
            "https://example.com/a.jpg?src=res.cloudinary.com/x/image/upload/",
        ):
            self.assertEqual(variant(url, 800), url)

    def test_variant_local_unchanged(self):
        self.assertEqual(variant("/media/proyectos/a.jpg", 800), "/media/proyectos/a.jpg")

    def test_srcset_widths(self):
        value = srcset(CLOUD)
        for width in (400, 800, 1600):
            self.assertIn(f"c_limit,w_{width}/v1/a.jpg {width}w", value)

    def test_srcset_local_has_descriptors(self):
        value = srcset("/media/a.jpg")
        for width in (400, 800, 1600):
            self.assertIn(f"{width}w", value)
