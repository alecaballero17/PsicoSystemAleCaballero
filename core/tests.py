from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from core.models import Clinica, Usuario, Paciente

class PsicoSystemAPITests(APITestCase):
    def setUp(self):
        # T005: Setup initial models
        self.clinica = Clinica.objects.create(
            nombre="Clínica Central",
            nit="12345678-9",
            direccion="Av. Busch, Santa Cruz"
        )
        self.user = Usuario.objects.create_user(
            username="psicologo_test",
            password="password123",
            email="test@psico.com",
            clinica=self.clinica,
            rol="PSICOLOGO"
        )
        self.login_url = reverse('api_login')
        self.paciente_url = reverse('api_pacientes_create')
        self.dashboard_url = reverse('api_dashboard')

    def test_login_jwt(self):
        """RF-01: Autenticación JWT"""
        data = {
            "username": "psicologo_test",
            "password": "password123"
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('role', response.data)
        self.assertEqual(response.data['role'], 'PSICOLOGO')

    def test_registrar_paciente_api(self):
        """T014: Registro de Paciente vía API"""
        # Login to get token
        login_response = self.client.post(self.login_url, {
            "username": "psicologo_test",
            "password": "password123"
        })
        token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        data = {
            "nombre": "Paciente de Prueba",
            "ci": "99887766",
            "fecha_nacimiento": "1995-10-10",
            "telefono": "77112233",
            "motivo_consulta": "Pruebas unitarias de API"
        }
        response = self.client.post(self.paciente_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # RF-29: Verificar aislamiento (Multi-tenancy)
        paciente = Paciente.objects.get(ci="99887766")
        self.assertEqual(paciente.clinica, self.clinica)

    def test_dashboard_api(self):
        """T008: Dashboard API"""
        login_response = self.client.post(self.login_url, {
            "username": "psicologo_test",
            "password": "password123"
        })
        token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['clinica'], "Clínica Central")
