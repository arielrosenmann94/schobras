"""Variantes responsivas de imágenes y dimensiones seguras para <img>."""
import logging

from django import template
from django.utils.html import format_html

register = template.Library()
logger = logging.getLogger(__name__)

WIDTHS = (400, 800, 1600)
CLOUDINARY_MARK = "res.cloudinary.com"
UPLOAD_SEGMENT = "/upload/"


@register.filter
def variant(url, width):
    """URL de la imagen al ancho pedido; en Cloudinary pide la variante, en local no cambia."""
    url = str(url or "")
    if CLOUDINARY_MARK not in url or UPLOAD_SEGMENT not in url:
        return url
    head, tail = url.split(UPLOAD_SEGMENT, 1)
    return f"{head}{UPLOAD_SEGMENT}f_auto,q_auto,w_{int(width)}/{tail}"


@register.filter
def srcset(url):
    """Valor de srcset con las variantes de 400, 800 y 1600 px."""
    return ", ".join(f"{variant(url, width)} {width}w" for width in WIDTHS)


@register.simple_tag
def image_size(image):
    """Atributos width y height de una imagen; vacío si el archivo no se puede leer."""
    try:
        width, height = image.width, image.height
    except (OSError, ValueError):
        logger.warning("No se pudieron leer las dimensiones de %s", getattr(image, "name", ""))
        return ""
    if not width or not height:
        return ""
    return format_html('width="{}" height="{}"', width, height)
