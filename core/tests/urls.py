"""URLconf solo para pruebas: vistas mínimas para inspeccionar cabeceras."""
from django.http import HttpResponse
from django.template import engines
from django.urls import path


def ping(request):
    return HttpResponse("ok")


def nonce_page(request):
    template = engines["django"].from_string("{{ csp_nonce }}")
    return HttpResponse(template.render({}, request))


urlpatterns = [
    path("ping/", ping),
    path("nonce/", nonce_page),
]
