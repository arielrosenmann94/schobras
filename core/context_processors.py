from projects.models import Project

from .models import SiteSettings
from .templatetags.site_tags import tel_digits
from .whatsapp import whatsapp_url


def site(request):
    """Datos globales del sitio para todas las plantillas."""
    settings_obj = SiteSettings.current()
    whatsapp_href = whatsapp_url(settings_obj.whatsapp, settings_obj.whatsapp_message)
    return {
        "site": settings_obj,
        "whatsapp_href": whatsapp_href,
        # Un teléfono sin dígitos no genera enlace tel:, así que no cuenta como canal.
        "has_contact": bool(whatsapp_href or tel_digits(settings_obj.phone) or settings_obj.email),
        "has_projects": Project.objects.published().exists(),
    }
