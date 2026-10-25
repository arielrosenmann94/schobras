from django.conf import settings
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
        "taxID": "77.897.204-2",
        "url": request.build_absolute_uri(reverse("core:home")),
        "areaServed": [{"@type": "AdministrativeArea", "name": name} for name in AREAS_SERVED],
    }
    if site.phone:
        data["telephone"] = site.phone
    if site.email:
        data["email"] = site.email
    return data


def _home_context(request):
    featured = (
        Project.objects.published()
        .filter(is_featured=True)
        .select_related("category")
        .prefetch_related("photos")[:FEATURED_LIMIT]
    )
    return {
        "featured_projects": featured,
        "jsonld": _organization_jsonld(request, SiteSettings.current()),
    }


def home(request):
    """Inicio: una página larga con anclas y hasta 6 proyectos destacados."""
    return render(request, "core/home.html", _home_context(request))


def home_v2(request):
    """Versión de diseño "del plano a la obra" (/v2/): mismo contenido que el inicio, sin indexar."""
    context = _home_context(request)
    context["nav_home"] = reverse("core:home_v2")
    return render(request, "core/home_v2.html", context)


@require_GET
def robots(request):
    if not settings.SEARCH_INDEXING:
        return HttpResponse("User-agent: *\nDisallow: /\n", content_type="text/plain")
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
