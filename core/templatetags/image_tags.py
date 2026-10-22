"""Variantes responsivas de imágenes y dimensiones seguras para <img>."""
import re

from django import template
from django.utils.html import format_html

register = template.Library()

WIDTHS = (400, 800, 1600)
CLOUDINARY_UPLOAD = re.compile(r"^https://res\.cloudinary\.com/[^/]+/image/upload/")


@register.filter
def variant(url, width):
    """URL de la imagen al ancho pedido; en Cloudinary pide la variante, en local no cambia."""
    url = str(url or "")
    match = CLOUDINARY_UPLOAD.match(url)
    if not match:
        return url
    return f"{match.group(0)}f_auto,q_auto,c_limit,w_{int(width)}/{url[match.end():]}"


@register.filter
def srcset(url):
    """Valor de srcset con las variantes de 400, 800 y 1600 px."""
    return ", ".join(f"{variant(url, width)} {width}w" for width in WIDTHS)


@register.simple_tag
def image_size(photo):
    """Atributos width y height guardados en la foto; nunca abre el archivo."""
    width, height = photo.image_width, photo.image_height
    if not width or not height:
        return ""
    return format_html('width="{}" height="{}"', width, height)
