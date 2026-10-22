"""URLconf solo para pruebas: vistas mínimas para inspeccionar cabeceras y plantillas."""
from django.http import HttpResponse
from django.shortcuts import render
from django.template import engines
from django.urls import path

CHILD_TEMPLATE = (
    '{% extends "base.html" %}'
    "{% block whatsapp_message %}Hola, vi el proyecto {{ title }} y quiero conversar uno parecido."
    "{% endblock %}"
)


def ping(request):
    return HttpResponse("ok")


def nonce_page(request):
    template = engines["django"].from_string("{{ csp_nonce }}")
    return HttpResponse(template.render({}, request))


def base_page(request):
    return render(request, "base.html")


def child_page(request):
    template = engines["django"].from_string(CHILD_TEMPLATE)
    return HttpResponse(template.render({"title": "Casa O'Higgins"}, request))


urlpatterns = [
    path("ping/", ping),
    path("nonce/", nonce_page),
    path("base/", base_page),
    path("hija/", child_page),
]
