"""Tags de la plantilla base: WhatsApp, teléfono, captura de bloques y SVG en línea."""
import html
import json
import re
from functools import lru_cache

from django import template
from django.contrib.staticfiles import finders
from django.core.serializers.json import DjangoJSONEncoder
from django.urls import reverse
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from core.whatsapp import normalize_number, whatsapp_url

register = template.Library()


@register.simple_tag(takes_context=True)
def whatsapp_href(context, message=""):
    """Enlace wa.me al número configurado; "" si no hay un número válido."""
    site = context.get("site")
    if site is None:
        return ""
    return whatsapp_url(site.whatsapp, message or site.whatsapp_message)


@register.simple_tag(takes_context=True)
def home_url(context):
    """Inicio al que apunta el menú: /v2/ lo cambia por el suyo (nav_home) para no salir de la versión."""
    return context.get("nav_home") or reverse("core:home")


@register.simple_tag
def brand_name(domain=True):
    """Marca con SCH en bronce (.brand__sch) para que no se lea "sobras".

    Junto solo como dominio (SCHOBRAS.CL); el nombre suelto va separado: SCH OBRAS.
    """
    if domain:
        return mark_safe('<span class="brand__sch">SCH</span>OBRAS.CL')
    return mark_safe('<span class="brand__sch">SCH</span> OBRAS')


@register.filter
def tel_digits(phone):
    """Número apto para un enlace tel:, con el + inicial y solo dígitos ("+56 (2) 2345-6789" → "+56223456789")."""
    phone = str(phone or "").strip()
    digits = re.sub(r"\D", "", phone)
    return f"+{digits}" if phone.startswith("+") and digits else digits


@register.filter
def wa_display(number):
    """Celular chileno legible ("912345678" → "+56 9 1234 5678"); si no es válido, el texto tal cual."""
    normalized = normalize_number(number)
    if not normalized:
        return str(number or "")
    return f"+{normalized[:2]} {normalized[2]} {normalized[3:7]} {normalized[7:]}"


@register.filter(needs_autoescape=True)
def email_wbr(email, autoescape=True):
    """Correo escapado con un punto de corte tras la "@", para que no se parta a mitad de palabra."""
    escape = conditional_escape if autoescape else str
    local, at, domain = str(email or "").partition("@")
    return mark_safe(f"{escape(local)}{at}<wbr>{escape(domain)}" if at else escape(local))


@register.filter(needs_autoescape=True)
def email_brand(email, autoescape=True):
    """Como email_wbr, pero en un dominio "schobras" envuelve el "sch" en .email-sch para darle
    otro color que a "obras", como en la marca. Cualquier otro correo queda igual que email_wbr."""
    escape = conditional_escape if autoescape else str
    local, at, domain = str(email or "").partition("@")
    start = domain.lower().find("schobras")
    if not at or start < 0:
        return email_wbr(email, autoescape)
    sch = f'<span class="email-sch">{escape(domain[start:start + 3])}</span>'
    branded = f"{escape(domain[:start])}{sch}{escape(domain[start + 3:])}"
    return mark_safe(f'<span class="email-brand">{escape(local)}@<wbr>{branded}</span>')


class CaptureNode(template.Node):
    # child_nodelists permite que {% block %} dentro de la captura siga siendo
    # sobrescribible por las plantillas hijas.
    child_nodelists = ("nodelist",)

    def __init__(self, nodelist, var_name):
        self.nodelist = nodelist
        self.var_name = var_name

    def render(self, context):
        text = html.unescape(self.nodelist.render(context))
        context[self.var_name] = " ".join(text.split())
        return ""


@register.tag
def capture(parser, token):
    """{% capture as nombre %}…{% endcapture %}: guarda el texto plano renderizado en una variable."""
    bits = token.split_contents()
    if len(bits) != 3 or bits[1] != "as":
        raise template.TemplateSyntaxError("Uso: {% capture as nombre %}…{% endcapture %}")
    nodelist = parser.parse(("endcapture",))
    parser.delete_first_token()
    return CaptureNode(nodelist, bits[2])


@lru_cache(maxsize=8)
def _read_svg(path):
    found = finders.find(path)
    if not found:
        raise template.TemplateSyntaxError(f"No existe el estático {path}")
    with open(found, encoding="utf-8") as svg_file:
        return re.sub(r"<\?xml[^>]*\?>|<!--.*?-->", "", svg_file.read(), flags=re.S).strip()


@register.simple_tag
def inline_svg(path):
    """Inserta un SVG estático del repositorio en línea (para currentColor y animación)."""
    return mark_safe(_read_svg(path))


_JSONLD_ESCAPES = {ord(">"): "\\u003E", ord("<"): "\\u003C", ord("&"): "\\u0026"}


@register.filter
def json_ld(value):
    """Serializa a JSON seguro para incrustar dentro de <script> (escapa <, > y &)."""
    return mark_safe(json.dumps(value, cls=DjangoJSONEncoder, ensure_ascii=False).translate(_JSONLD_ESCAPES))
