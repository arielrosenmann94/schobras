from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views import defaults
from django.views.decorators.http import require_GET

from projects.models import Project

from .models import SiteSettings

FEATURED_LIMIT = 6
AREAS_SERVED = [
    "Región Metropolitana de Santiago",
    "Región de Valparaíso",
    "Región del Libertador General Bernardo O'Higgins",
]


def _organization_jsonld(request, site):
    """Datos estructurados de la empresa; teléfono y correo solo si están configurados."""
    data = {
        "@context": "https://schema.org",
        "@type": "GeneralContractor",
        "name": "SCHOBRAS.CL",
        "legalName": "Constructora Schonffeldt SpA",
        "url": request.build_absolute_uri(reverse("core:home")),
        "areaServed": [{"@type": "AdministrativeArea", "name": name} for name in AREAS_SERVED],
    }
    if site.phone:
        data["telephone"] = site.phone
    if site.email:
        data["email"] = site.email
    return data


def home(request):
    """Inicio: una página larga con anclas y hasta 6 proyectos destacados."""
    featured = (
        Project.objects.published()
        .filter(is_featured=True)
        .select_related("category")
        .prefetch_related("photos")[:FEATURED_LIMIT]
    )
    return render(
        request,
        "core/home.html",
        {
            "featured_projects": featured,
            "jsonld": _organization_jsonld(request, SiteSettings.current()),
        },
    )


@require_GET
def robots(request):
    lines = [
        "User-agent: *",
        "Disallow: /panel/",
        f"Sitemap: {request.build_absolute_uri(reverse('core:sitemap'))}",
        "",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def permission_denied(request, exception):
    """403: en el panel con el diseño del panel; en el resto, con el del sitio público."""
    template_name = "403.html"
    if request.path.startswith(reverse("panel:home")):
        template_name = "panel/403.html"
    return defaults.permission_denied(request, exception, template_name=template_name)
