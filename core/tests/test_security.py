from django.test import TestCase, override_settings


@override_settings(ROOT_URLCONF="core.tests.urls")
class SecurityHeadersTests(TestCase):
    def test_csp_header_present(self):
        response = self.client.get("/ping/")
        csp = response["Content-Security-Policy"]
        self.assertIn("frame-ancestors 'none'", csp)
        self.assertNotIn("unsafe-inline", csp)
        self.assertIn("script-src 'self'", csp)
        self.assertIn("img-src 'self' data: https://res.cloudinary.com", csp)

    def test_security_headers(self):
        response = self.client.get("/ping/")
        self.assertEqual(response["X-Frame-Options"], "DENY")
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")
        self.assertEqual(response["Referrer-Policy"], "strict-origin-when-cross-origin")

    def test_csp_nonce_available_in_templates(self):
        response = self.client.get("/nonce/")
        nonce = response.content.decode()
        self.assertTrue(nonce)
        self.assertIn(f"'nonce-{nonce}'", response["Content-Security-Policy"])
