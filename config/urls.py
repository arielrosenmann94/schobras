"""Rutas de SCHOBRAS.CL."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("panel/", include("panel.urls")),
    path("proyectos/", include("projects.urls")),
    path("", include("core.urls")),
]

handler403 = "core.views.permission_denied"

# Solo en local: runserver sirve las fotos subidas. En producción van a Cloudinary.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
