"""Tags de la plantilla base: WhatsApp, teléfono, captura de bloques y SVG en línea."""
import html
import re
from functools import lru_cache

from django import template
from django.contrib.staticfiles import finders
from django.utils.safestring import mark_safe

from core.whatsapp import whatsapp_url

register = template.Library()


@register.simple_tag(takes_context=True)
def whatsapp_href(context, message=""):
    """Enlace wa.me al número configurado; "" si no hay un número válido."""
    site = context.get("site")
    if site is None:
        return ""
    return whatsapp_url(site.whatsapp, message or site.whatsapp_message)


@register.filter
def tel_digits(phone):
    """Número apto para un enlace tel:, con el + inicial y solo dígitos ("+56 (2) 2345-6789" → "+56223456789")."""
    phone = str(phone or "").strip()
    digits = re.sub(r"\D", "", phone)
    return f"+{digits}" if phone.startswith("+") and digits else digits


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
