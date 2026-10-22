from django.utils.text import slugify


def unique_slug(model, text: str, max_length: int = 170) -> str:
    """Devuelve un slug único para `model` a partir de `text`.

    Los duplicados reciben sufijo -2, -3... y el resultado nunca supera
    `max_length` (se recorta la base antes de agregar el sufijo).
    """
    base = slugify(text)[:max_length].strip("-") or "item"
    candidate = base
    counter = 2
    while model.objects.filter(slug=candidate).exists():
        suffix = f"-{counter}"
        candidate = f"{base[: max_length - len(suffix)].rstrip('-')}{suffix}"
        counter += 1
    return candidate
