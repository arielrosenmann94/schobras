import os
import subprocess
import sys

from django.conf import settings
from django.test import SimpleTestCase


class ProductionAdminUrlTests(SimpleTestCase):
    """QA-1.9: en producción ADMIN_URL es obligatoria y no puede ser admin/.

    Se importa production.py en otro proceso: importarlo aquí modificaría las
    listas y diccionarios de base.py que usan las pruebas (MIDDLEWARE, STORAGES).
    """

    def import_production(self, admin_url):
        env = {
            **os.environ,
            "SECRET_KEY": "x" * 50,
            "CLOUDINARY_URL": "cloudinary://key:secret@demo",
            "DATABASE_URL": "sqlite:///:memory:",
            "ADMIN_URL": admin_url,
        }
        return subprocess.run(
            [sys.executable, "-c", "import config.settings.production"],
            cwd=settings.BASE_DIR,
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
        )

    def test_rejects_empty_or_default_admin_url(self):
        for value in ["", "admin/", "/admin/", "admin"]:
            with self.subTest(value=value):
                result = self.import_production(value)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("ImproperlyConfigured", result.stderr)
                self.assertIn("ADMIN_URL", result.stderr)

    def test_rejects_admin_url_without_trailing_slash(self):
        # QA-2.5: "gestion" dejaba el admin en /gestionlogin/; con "/" al
        # inicio la ruta nunca coincide (Django quita esa barra de la URL).
        for value in ["gestion-x7k2", "/gestion-x7k2", "/gestion-x7k2/"]:
            with self.subTest(value=value):
                result = self.import_production(value)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("ImproperlyConfigured", result.stderr)
                self.assertIn("terminar en /", result.stderr)

    def test_accepts_custom_admin_url(self):
        result = self.import_production("gestion-x7k2/")
        self.assertEqual(result.returncode, 0, result.stderr)


class ProductionSearchIndexingTests(SimpleTestCase):
    """Sin dominio propio (herokuapp) la web no se indexa hasta que se active SEARCH_INDEXING."""

    def production_value(self, **extra):
        env = {
            key: value for key, value in os.environ.items() if key != "SEARCH_INDEXING"
        }
        env.update(
            SECRET_KEY="x" * 50,
            CLOUDINARY_URL="cloudinary://key:secret@demo",
            DATABASE_URL="sqlite:///:memory:",
            ADMIN_URL="gestion-x7k2/",
            **extra,
        )
        result = subprocess.run(
            [sys.executable, "-c", "import sys, config.settings.production as p; sys.stdout.write(str(p.SEARCH_INDEXING))"],
            cwd=settings.BASE_DIR,
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def test_indexing_off_by_default(self):
        self.assertEqual(self.production_value(), "False")

    def test_indexing_on_when_enabled(self):
        self.assertEqual(self.production_value(SEARCH_INDEXING="True"), "True")
