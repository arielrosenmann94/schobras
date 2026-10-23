"""Revisión humana de Ariel, ronda 1: fondo de plano sin ejes interiores (A1)."""
import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


def read(relative):
    return (Path(settings.BASE_DIR) / relative).read_text(encoding="utf-8")


def plan_block(css):
    """Bloque «Plano» de site.css: desde su título hasta la sección siguiente."""
    start = css.index("/* ── Plano:")
    return css[start:css.index("/* ──", start + 1)]


class AxesBackgroundTests(SimpleTestCase):
    def test_no_interior_axes_declared(self):
        block = plan_block(read("static/css/site.css"))
        for interior in ("25% 0", "50% 0 / 1px", "75% 0"):
            self.assertNotIn(interior, block)
        self.assertNotIn("linear-gradient", block)

    def test_frame_keeps_its_two_borders(self):
        self.assertIn("border-inline: 1px solid", plan_block(read("static/css/site.css")))

    def test_frame_sits_outside_the_content(self):
        """El marco es medio margen más ancho que el contenido por lado: nunca toca una letra."""
        block = plan_block(read("static/css/site.css"))
        rule = re.search(r"body::before,\s*\.axes::before\s*\{([^}]*)\}", block).group(1)
        self.assertNotIn("100% - 2 * var(--gutter)", rule)
        self.assertIn("width: min(100% - var(--gutter), var(--max-width) - var(--gutter))", rule)
