from django.core.exceptions import ValidationError
from django.test import RequestFactory, SimpleTestCase, TestCase

from core.context_processors import site
from core.models import SiteSettings
from core.whatsapp import normalize_number, whatsapp_url


class WhatsAppTests(SimpleTestCase):
    def test_normalize_chilean_formats(self):
        for raw in ("+56 9 1234 5678", "912345678", "56912345678", "+56-9-1234-5678"):
            with self.subTest(raw=raw):
                self.assertEqual(normalize_number(raw), "56912345678")

    def test_normalize_invalid_returns_empty(self):
        for raw in ("", "123", "hola"):
            with self.subTest(raw=raw):
                self.assertEqual(normalize_number(raw), "")

    def test_whatsapp_url(self):
        self.assertEqual(
            whatsapp_url("912345678", "Hola, quiero"),
            "https://wa.me/56912345678?text=Hola%2C%20quiero",
        )
        self.assertEqual(whatsapp_url("123", "Hola"), "")

    def test_whatsapp_url_encodes_slash(self):
        self.assertEqual(
            whatsapp_url("912345678", "Casa 1/2"),
            "https://wa.me/56912345678?text=Casa%201%2F2",
        )


class SiteSettingsTests(TestCase):
    def test_load_is_singleton(self):
        first = SiteSettings.load()
        second = SiteSettings.load()
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(SiteSettings.objects.count(), 1)
        self.assertEqual(first.whatsapp_message, "Hola, quiero conversar sobre un proyecto.")

    def test_second_row_is_rejected(self):
        SiteSettings.load()
        with self.assertRaises(ValidationError):
            SiteSettings(email="otro@example.com").save()
        self.assertEqual(SiteSettings.objects.count(), 1)

    def test_existing_row_can_be_saved_again(self):
        settings_obj = SiteSettings.load()
        settings_obj.phone = "+56 2 2345 6789"
        settings_obj.save()
        self.assertEqual(SiteSettings.objects.count(), 1)


class SiteContextTests(TestCase):
    def context(self):
        return site(RequestFactory().get("/"))

    def test_context_empty(self):
        ctx = self.context()
        self.assertEqual(ctx["whatsapp_href"], "")
        self.assertFalse(ctx["has_contact"])
        self.assertFalse(ctx["has_projects"])

    def test_context_does_not_write_to_db(self):
        self.context()
        self.assertEqual(SiteSettings.objects.count(), 0)

    def test_context_email_only(self):
        settings_obj = SiteSettings.load()
        settings_obj.email = "oficina@example.com"
        settings_obj.save()
        ctx = self.context()
        self.assertTrue(ctx["has_contact"])
        self.assertEqual(ctx["whatsapp_href"], "")

    def test_context_invalid_whatsapp_alone_is_not_contact(self):
        settings_obj = SiteSettings.load()
        settings_obj.whatsapp = "123"
        settings_obj.save()
        ctx = self.context()
        self.assertFalse(ctx["has_contact"])
        self.assertEqual(ctx["whatsapp_href"], "")

    def test_context_valid_whatsapp(self):
        settings_obj = SiteSettings.load()
        settings_obj.whatsapp = "912345678"
        settings_obj.save()
        ctx = self.context()
        self.assertTrue(ctx["has_contact"])
        self.assertTrue(ctx["whatsapp_href"].startswith("https://wa.me/56912345678?text="))
