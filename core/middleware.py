from django.conf import settings
from django.http import HttpResponsePermanentRedirect

CANONICAL_HOST = "schobras.cl"
WWW_HOST = "www.schobras.cl"


class CanonicalHostMiddleware:
    """Redirige www.schobras.cl a https://schobras.cl conservando ruta y query."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.META.get("HTTP_HOST", "").split(":")[0].lower()
        if host == WWW_HOST:
            return HttpResponsePermanentRedirect(f"https://{CANONICAL_HOST}{request.get_full_path()}")
        return self.get_response(request)


class NoIndexMiddleware:
    """Con SEARCH_INDEXING apagado (web en herokuapp, sin dominio propio) pide a los buscadores no indexar."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if not settings.SEARCH_INDEXING:
            response.headers["X-Robots-Tag"] = "noindex, nofollow"
        return response
