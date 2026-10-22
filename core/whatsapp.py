import re
from urllib.parse import quote


def normalize_number(number: str) -> str:
    """Normaliza un celular chileno a 569XXXXXXXX; devuelve "" si es inválido."""
    digits = re.sub(r"\D", "", number or "")
    if len(digits) == 11 and digits.startswith("569"):
        return digits
    if len(digits) == 9 and digits.startswith("9"):
        return "56" + digits
    return ""


def whatsapp_url(number: str, message: str) -> str:
    """Enlace wa.me con el mensaje precargado; "" si el número es inválido."""
    normalized = normalize_number(number)
    if not normalized:
        return ""
    return f"https://wa.me/{normalized}?text={quote(message or '')}"
