from projects.models import Project

from .models import SiteSettings
from .whatsapp import whatsapp_url


def site(request):
    """Datos globales del sitio para todas las plantillas."""
    settings_obj = SiteSettings.load()
    whatsapp_href = whatsapp_url(settings_obj.whatsapp, settings_obj.whatsapp_message)
    return {
        "site": settings_obj,
        "whatsapp_href": whatsapp_href,
        "has_contact": bool(whatsapp_href or settings_obj.phone or settings_obj.email),
        "has_projects": Project.objects.published().exists(),
    }
