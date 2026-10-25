from django.contrib.sitemaps.views import sitemap
from django.urls import path
from django.views.generic import RedirectView

from . import views
from .sitemaps import ProjectSitemap, StaticSitemap

app_name = "core"

sitemaps = {"static": StaticSitemap, "projects": ProjectSitemap}

urlpatterns = [
    path("", views.home, name="home"),
    # /v2/ fue la exploración de diseño que pasó a ser el inicio (2026-10-25).
    path("v2/", RedirectView.as_view(pattern_name="core:home", permanent=True)),
    path("sch/", views.brand_options, name="brand_options"),
    path("robots.txt", views.robots, name="robots"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
]
