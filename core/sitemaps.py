from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from projects.models import Project


class StaticSitemap(Sitemap):
    """Inicio y lista de proyectos."""

    changefreq = "monthly"

    def items(self):
        return ["core:home", "projects:list"]

    def location(self, item):
        return reverse(item)


class ProjectSitemap(Sitemap):
    """Solo proyectos públicos (publicados y con fotos)."""

    changefreq = "monthly"

    def items(self):
        return Project.objects.published().order_by("-created_at")

    def lastmod(self, obj):
        return obj.updated_at
