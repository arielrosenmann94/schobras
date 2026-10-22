from django.contrib.sitemaps.views import sitemap
from django.urls import path

from . import views
from .sitemaps import ProjectSitemap, StaticSitemap

app_name = "core"

sitemaps = {"static": StaticSitemap, "projects": ProjectSitemap}

urlpatterns = [
    path("", views.home, name="home"),
    path("robots.txt", views.robots, name="robots"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
]
