from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase

from core.middleware import CanonicalHostMiddleware


def ok_view(request):
    return HttpResponse("ok")


class CanonicalHostMiddlewareTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = CanonicalHostMiddleware(ok_view)

    def test_www_redirects_to_apex_keeping_path_and_query(self):
        request = self.factory.get("/proyectos/casa/?categoria=residencial", HTTP_HOST="www.schobras.cl")
        response = self.middleware(request)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response["Location"], "https://schobras.cl/proyectos/casa/?categoria=residencial")

    def test_www_root_without_query(self):
        request = self.factory.get("/", HTTP_HOST="www.schobras.cl")
        response = self.middleware(request)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response["Location"], "https://schobras.cl/")

    def test_www_with_port_redirects(self):
        request = self.factory.get("/", HTTP_HOST="www.schobras.cl:443")
        self.assertEqual(self.middleware(request).status_code, 301)

    def test_apex_passes_through(self):
        request = self.factory.get("/", HTTP_HOST="schobras.cl")
        self.assertEqual(self.middleware(request).status_code, 200)

    def test_other_hosts_pass_through(self):
        request = self.factory.get("/", HTTP_HOST="schobras.herokuapp.com")
        self.assertEqual(self.middleware(request).status_code, 200)
