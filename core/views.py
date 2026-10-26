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
        "name": "SCHobras.cl",
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


def home(request):
    """Inicio: una página larga con anclas y hasta 6 proyectos destacados."""
    featured = (
        Project.objects.published()
        .filter(is_featured=True)
        .select_related("category")
        .prefetch_related("photos")[:FEATURED_LIMIT]
    )
    context = {
        "featured_projects": featured,
        "jsonld": _organization_jsonld(request, SiteSettings.current()),
    }
    return render(request, "core/home.html", context)


# Formas de escribir la marca para que no se lea "sobras" (página /sch/, para decidir).
# sch, sep y obras se escriben tal cual se ven; cl es el dominio. La 2 es la propuesta de Claudia.
BRAND_OPTIONS = [
    {"name": "La actual", "text": "SCH en bronce y OBRAS en antracita, todo en mayúsculas y espaciado.",
     "sch": "SCH", "sep": "", "obras": "OBRAS", "cl": ".CL"},
    {"name": "La propuesta de Claudia", "text": "SCH en mayúsculas y obras en minúsculas, en el bronce del logo. Se distinguen sin separarse.",
     "sch": "SCH", "sep": "", "obras": "obras", "cl": ".cl"},
    {"name": "Mayúsculas y minúsculas", "text": "Un solo color: la diferencia la hace el tamaño de las letras.",
     "sch": "SCH", "sep": "", "obras": "obras", "cl": ".cl"},
    {"name": "SCH en bronce, obras en minúsculas", "text": "Como la de Claudia, con los colores al revés.",
     "sch": "SCH", "sep": "", "obras": "obras", "cl": ".cl"},
    {"name": "Contraste de peso", "text": "SCH en negrita y obras en trazo fino, del mismo color.",
     "sch": "SCH", "sep": "", "obras": "obras", "cl": ".cl"},
    {"name": "Punto medio", "text": "Un punto en bronce entre SCH y OBRAS.",
     "sch": "SCH", "sep": "·", "obras": "OBRAS", "cl": ".CL"},
    {"name": "Línea de eje", "text": "Una línea fina en bronce, como un eje del plano.",
     "sch": "SCH", "sep": "", "obras": "OBRAS", "cl": ".CL"},
    {"name": "Dos palabras", "text": "SCH OBRAS con un espacio, como en el título «Por qué SCH OBRAS».",
     "sch": "SCH", "sep": " ", "obras": "OBRAS", "cl": ".CL"},
    {"name": "SCH en bloque", "text": "SCH sobre un bloque antracita, como un muro.",
     "sch": "SCH", "sep": "", "obras": "OBRAS", "cl": ".CL"},
    {"name": "SCH con cota", "text": "Una línea en bronce bajo SCH, como una cota del plano.",
     "sch": "SCH", "sep": "", "obras": "OBRAS", "cl": ".CL"},
    {"name": "Apilada", "text": "SCH sobre OBRAS, para espacios cuadrados como un sello o una foto de perfil.",
     "sch": "SCH", "sep": "", "obras": "OBRAS", "cl": ".CL"},
    {"name": "Todo en minúsculas", "text": "sch en negrita y bronce, obras en trazo fino.",
     "sch": "sch", "sep": "", "obras": "obras", "cl": ".cl"},
]


def brand_options(request):
    """/sch/: las formas de escribir SCHOBRAS una al lado de la otra, para elegir (sin indexar)."""
    return render(request, "core/sch.html", {"options": BRAND_OPTIONS})


def privacy(request):
    """/privacidad/: para qué se usan los datos de quien escribe (no hay formularios ni analítica)."""
    return render(request, "core/privacy.html")


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
