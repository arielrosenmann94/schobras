import importlib
import shutil
import tempfile
from pathlib import Path

from django.test import TestCase, override_settings
from django.urls import clear_url_caches

import config.urls


def reload_urls():
    importlib.reload(config.urls)
    clear_url_caches()


class MediaInDebugTests(TestCase):
    """En local (DEBUG) runserver sirve las fotos subidas; en producción no."""

    def setUp(self):
        media = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, media, ignore_errors=True)
        Path(media, "foto.jpg").write_bytes(b"jpeg")
        self.media = media
        self.addCleanup(reload_urls)

    def test_media_served_with_debug(self):
        with override_settings(DEBUG=True, MEDIA_ROOT=self.media):
            reload_urls()
            response = self.client.get("/media/foto.jpg")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(b"".join(response.streaming_content), b"jpeg")

    def test_media_not_served_without_debug(self):
        with override_settings(DEBUG=False, MEDIA_ROOT=self.media):
            reload_urls()
            self.assertEqual(self.client.get("/media/foto.jpg").status_code, 404)
