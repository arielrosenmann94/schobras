"""Rutas de SCHOBRAS.CL."""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("panel/", include("panel.urls")),
    path("proyectos/", include("projects.urls")),
    path("", include("core.urls")),
]
