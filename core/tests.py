from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status


class PsicoSystemSmokeTest(TestCase):
    """
    T009: Verificación de estándares de calidad y disponibilidad de API.
    """

    def setUp(self):
        self.client = APIClient()

    def test_api_status_unauthenticated(self):
        # Verifica que la seguridad (RNF-03) bloquee accesos sin token
        response = self.client.get("/api/dashboard/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
