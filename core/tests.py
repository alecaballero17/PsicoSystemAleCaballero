"""
PsicoSystem SI2 — Suite de Pruebas Automatizadas.
[SPRINT 0 - T004] Validación del entorno de testing.
[SPRINT 1 - T011] Tests de autenticación JWT (RF-01).
[SPRINT 1 - T014] Tests de registro de pacientes (RF-02).
[SPRINT 1 - T018] Tests RBAC (RF-28).
[SPRINT 1 - T022] Tests de blacklist JWT (CU-04).
[SPRINT 1 - T024] Tests de registro de clínica (RF-29).
Cobertura objetivo: ≥ 70% en módulos Auth y Tenants.
"""

from django.urls import reverse
from django.db import IntegrityError
from rest_framework import status
from rest_framework.test import APITestCase
from core.models import Clinica, Usuario, Paciente, Cita
import logging

logger = logging.getLogger(__name__)


# ==============================================================================
# BLOQUE 1: TESTS UNITARIOS DE MODELOS [SPRINT 0 - T005]
# ==============================================================================
class ModelUnitTests(APITestCase):
    """Valida la integridad del esquema ER y las restricciones de campo."""

    def setUp(self):
        self.clinica = Clinica.objects.create(
            nombre="Clínica Test Modelos",
            nit="MODEL-001",
            direccion="Av. Test 100",
        )

    def test_clinica_str(self):
        """[SPRINT 0 - T005] Verifica la representación string del modelo Clinica."""
        self.assertEqual(str(self.clinica), "Clínica Test Modelos")

    def test_usuario_requiere_clinica(self):
        """[SPRINT 0 - T005] [RF-29] Verifica que un usuario no-admin requiere clínica."""
        usuario = Usuario.objects.create_user(
            username="user_con_clinica",
            password="test123",
            clinica=self.clinica,
            rol="PSICOLOGO",
        )
        self.assertEqual(usuario.clinica, self.clinica)
        self.assertEqual(usuario.rol, "PSICOLOGO")

    def test_paciente_ci_unico(self):
        """[SPRINT 0 - T005] Verifica la restricción UNIQUE en CI del paciente."""
        Paciente.objects.create(
            clinica=self.clinica,
            nombre="Paciente Original",
            ci="UNIQUE-001",
            fecha_nacimiento="1990-01-01",
            telefono="70000001",
            motivo_consulta="Test de unicidad",
        )
        with self.assertRaises(IntegrityError):
            Paciente.objects.create(
                clinica=self.clinica,
                nombre="Paciente Duplicado",
                ci="UNIQUE-001",
                fecha_nacimiento="1991-02-02",
                telefono="70000002",
                motivo_consulta="Intento duplicado",
            )

    def test_paciente_pertenece_a_clinica(self):
        """[SPRINT 0 - T005] [RF-29] FK Multi-tenant: paciente vinculado a clínica."""
        paciente = Paciente.objects.create(
            clinica=self.clinica,
            nombre="Paciente Vinculado",
            ci="TENANT-001",
            fecha_nacimiento="1988-06-15",
            telefono="70000003",
            motivo_consulta="Pertenencia de tenant",
        )
        self.assertEqual(paciente.clinica.id, self.clinica.id)

    def test_cita_modelo_completo(self):
        """[SPRINT 0 - T005] Verifica la creación de citas con todas las FK."""
        psicologo = Usuario.objects.create_user(
            username="psicologo_cita",
            password="test123",
            clinica=self.clinica,
            rol="PSICOLOGO",
        )
        paciente = Paciente.objects.create(
            clinica=self.clinica,
            nombre="Paciente Cita",
            ci="CITA-001",
            fecha_nacimiento="1992-03-20",
            telefono="70000004",
            motivo_consulta="Cita de prueba",
        )
        cita = Cita.objects.create(
            paciente=paciente,
            psicologo=psicologo,
            fecha_hora="2026-04-15T10:00:00Z",
            motivo="Sesión inicial de evaluación",
            estado="PENDIENTE",
        )
        self.assertEqual(cita.paciente, paciente)
        self.assertEqual(cita.psicologo, psicologo)
        self.assertEqual(cita.estado, "PENDIENTE")


# ==============================================================================
# BLOQUE 2: TESTS DE AUTENTICACIÓN JWT [SPRINT 1 - T011]
# ==============================================================================
class AuthJWTTests(APITestCase):
    """Valida el flujo completo de autenticación stateless (RF-01, CU-01)."""

    def setUp(self):
        self.clinica = Clinica.objects.create(
            nombre="Clínica Auth",
            nit="AUTH-001",
            direccion="Av. Seguridad 200",
        )
        self.user = Usuario.objects.create_user(
            username="psicologo_auth",
            password="password123",
            email="auth@psico.com",
            clinica=self.clinica,
            rol="PSICOLOGO",
        )
        self.login_url = reverse("api_login")

    def test_login_jwt_exitoso(self):
        """[SPRINT 1 - T011] [RF-01] Login devuelve access, refresh, role y clinica."""
        data = {"username": "psicologo_auth", "password": "password123"}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("role", response.data)
        self.assertEqual(response.data["role"], "PSICOLOGO")
        self.assertEqual(response.data["clinica_nombre"], "Clínica Auth")

    def test_login_credenciales_invalidas(self):
        """[SPRINT 1 - T011] [RF-01] Login con credenciales incorrectas devuelve 401."""
        data = {"username": "psicologo_auth", "password": "wrong_password"}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_usuario_inexistente(self):
        """[SPRINT 1 - T011] [RF-01] Login con usuario que no existe devuelve 401."""
        data = {"username": "fantasma", "password": "nada"}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_endpoint_autenticado(self):
        """[SPRINT 1 - T011] [CU-01] Endpoint /me/ retorna datos del usuario autenticado."""
        login_resp = self.client.post(
            self.login_url, {"username": "psicologo_auth", "password": "password123"}
        )
        token = login_resp.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)

        me_url = reverse("api_me")
        response = self.client.get(me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "psicologo_auth")

    def test_me_endpoint_sin_token(self):
        """[SPRINT 1 - T011] [RNF-03] /me/ sin token devuelve 401."""
        me_url = reverse("api_me")
        response = self.client.get(me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# ==============================================================================
# BLOQUE 3: TESTS DE LOGOUT / BLACKLIST [SPRINT 1 - T022]
# ==============================================================================
class LogoutBlacklistTests(APITestCase):
    """Valida la revocación de tokens JWT (CU-04, T022)."""

    def setUp(self):
        self.clinica = Clinica.objects.create(
            nombre="Clínica Logout",
            nit="LOGOUT-001",
            direccion="Av. Blacklist 300",
        )
        self.user = Usuario.objects.create_user(
            username="user_logout",
            password="password123",
            clinica=self.clinica,
            rol="PSICOLOGO",
        )
        self.login_url = reverse("api_login")
        self.logout_url = reverse("api_logout")

    def test_logout_exitoso(self):
        """[SPRINT 1 - T022] [CU-04] Logout invalida el refresh token."""
        login_resp = self.client.post(
            self.login_url, {"username": "user_logout", "password": "password123"}
        )
        access = login_resp.data["access"]
        refresh = login_resp.data["refresh"]

        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access)
        response = self.client.post(self.logout_url, {"refresh": refresh})
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

    def test_logout_sin_refresh_token(self):
        """[SPRINT 1 - T022] [CU-04] Logout sin refresh token devuelve 400."""
        login_resp = self.client.post(
            self.login_url, {"username": "user_logout", "password": "password123"}
        )
        access = login_resp.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access)
        response = self.client.post(self.logout_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_doble_logout_falla(self):
        """[SPRINT 1 - T022] [CU-04] Usar refresh ya invalidado devuelve error."""
        login_resp = self.client.post(
            self.login_url, {"username": "user_logout", "password": "password123"}
        )
        access = login_resp.data["access"]
        refresh = login_resp.data["refresh"]
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access)

        # Primer logout: éxito
        self.client.post(self.logout_url, {"refresh": refresh})
        # Segundo logout con el mismo token: debe fallar
        response = self.client.post(self.logout_url, {"refresh": refresh})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# ==============================================================================
# BLOQUE 4: TESTS RBAC [SPRINT 1 - T018]
# ==============================================================================
class RBACTests(APITestCase):
    """Valida el control de acceso basado en roles (RF-28, T018)."""

    def setUp(self):
        self.clinica = Clinica.objects.create(
            nombre="Clínica RBAC",
            nit="RBAC-001",
            direccion="Av. Permisos 400",
        )
        self.admin = Usuario.objects.create_user(
            username="admin_rbac",
            password="password123",
            clinica=self.clinica,
            rol="ADMIN",
        )
        self.psicologo = Usuario.objects.create_user(
            username="psico_rbac",
            password="password123",
            clinica=self.clinica,
            rol="PSICOLOGO",
        )
        self.login_url = reverse("api_login")

    def _get_token(self, username):
        """Helper: obtiene el access token de un usuario."""
        resp = self.client.post(
            self.login_url, {"username": username, "password": "password123"}
        )
        return resp.data["access"]

    def test_admin_puede_crear_clinica(self):
        """[SPRINT 1 - T018] [RF-28] Un ADMIN puede registrar una clínica nueva."""
        token = self._get_token("admin_rbac")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)

        data = {"nombre": "Nueva Clínica", "nit": "NEW-001", "direccion": "Av. Nueva"}
        url = reverse("api_registrar_clinica")
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_psicologo_no_puede_crear_clinica(self):
        """[SPRINT 1 - T018] [RF-28] Un PSICOLOGO NO puede registrar clínicas."""
        token = self._get_token("psico_rbac")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)

        data = {"nombre": "Intento", "nit": "HACK-001", "direccion": "Av. Prohibida"}
        url = reverse("api_registrar_clinica")
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_psicologo_no_puede_crear_usuario(self):
        """[SPRINT 1 - T018] [RF-28] Un PSICOLOGO NO puede crear usuarios."""
        token = self._get_token("psico_rbac")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)

        data = {
            "username": "hacker",
            "password": "password123",
            "email": "h@psico.com",
            "rol": "ADMIN",
            "clinica": self.clinica.id,
        }
        url = reverse("api_registrar_usuario")
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_puede_crear_usuario(self):
        """[SPRINT 1 - T018] [RF-28] Un ADMIN puede crear usuarios."""
        token = self._get_token("admin_rbac")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)

        data = {
            "username": "nuevo_psico",
            "password": "password123",
            "email": "new@psico.com",
            "rol": "PSICOLOGO",
            "clinica": self.clinica.id,
        }
        url = reverse("api_registrar_usuario")
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


# ==============================================================================
# BLOQUE 5: TESTS DE REGISTRO DE PACIENTES [SPRINT 1 - T014]
# ==============================================================================
class PacienteRegistroTests(APITestCase):
    """Valida los endpoints de registro y listado de pacientes (RF-02, CU-02)."""

    def setUp(self):
        self.clinica = Clinica.objects.create(
            nombre="Clínica Pacientes",
            nit="PAC-001",
            direccion="Av. Pacientes 500",
        )
        self.psicologo = Usuario.objects.create_user(
            username="psico_pacientes",
            password="password123",
            clinica=self.clinica,
            rol="PSICOLOGO",
        )
        self.login_url = reverse("api_login")

    def _auth(self):
        resp = self.client.post(
            self.login_url,
            {"username": "psico_pacientes", "password": "password123"},
        )
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + resp.data["access"])

    def test_registrar_paciente_exitoso(self):
        """[SPRINT 1 - T014] [RF-02] Registro de paciente asigna clínica automáticamente."""
        self._auth()
        data = {
            "nombre": "Juan Pérez",
            "ci": "REG-001",
            "fecha_nacimiento": "1995-05-15",
            "telefono": "77712345",
            "motivo_consulta": "Ansiedad generalizada",
        }
        url = reverse("api_pacientes_create")
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # RF-29: Verificar aislamiento multi-tenant
        paciente = Paciente.objects.get(ci="REG-001")
        self.assertEqual(paciente.clinica.id, self.clinica.id)

    def test_registrar_paciente_ci_duplicado(self):
        """[SPRINT 1 - T014] Registro con CI duplicado devuelve error."""
        self._auth()
        data = {
            "nombre": "Primer Paciente",
            "ci": "DUP-001",
            "fecha_nacimiento": "1990-01-01",
            "telefono": "70000001",
            "motivo_consulta": "Primera consulta",
        }
        url = reverse("api_pacientes_create")
        self.client.post(url, data)

        # Segundo intento con mismo CI
        data["nombre"] = "Duplicado"
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_listar_pacientes_autenticado(self):
        """[SPRINT 1 - T014] Listado de pacientes requiere autenticación."""
        self._auth()
        url = reverse("api_pacientes_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_listar_pacientes_sin_auth(self):
        """[SPRINT 1 - T014] [RNF-03] Listado sin token devuelve 401."""
        url = reverse("api_pacientes_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_registrar_paciente_sin_auth(self):
        """[SPRINT 1 - T014] [RNF-03] Registro sin token devuelve 401."""
        data = {
            "nombre": "Sin Auth",
            "ci": "NOAUTH-001",
            "fecha_nacimiento": "1990-01-01",
            "telefono": "70000001",
            "motivo_consulta": "Intento sin autenticación",
        }
        url = reverse("api_pacientes_create")
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# ==============================================================================
# BLOQUE 6: TESTS DE AISLAMIENTO MULTI-TENANT [SPRINT 1 - T024]
# ==============================================================================
class MultiTenantIsolationTests(APITestCase):
    """Valida que los datos de una clínica son invisibles para otra (RF-29)."""

    def setUp(self):
        # Crear dos clínicas independientes
        self.clinica_a = Clinica.objects.create(
            nombre="Clínica Alpha", nit="ALPHA-001", direccion="Zona Norte"
        )
        self.clinica_b = Clinica.objects.create(
            nombre="Clínica Beta", nit="BETA-001", direccion="Zona Sur"
        )
        # Psicólogos en cada clínica
        self.psico_a = Usuario.objects.create_user(
            username="psico_alpha",
            password="password123",
            clinica=self.clinica_a,
            rol="PSICOLOGO",
        )
        self.psico_b = Usuario.objects.create_user(
            username="psico_beta",
            password="password123",
            clinica=self.clinica_b,
            rol="PSICOLOGO",
        )
        # Pacientes en cada clínica
        Paciente.objects.create(
            clinica=self.clinica_a,
            nombre="Paciente Alpha",
            ci="ISO-A01",
            fecha_nacimiento="1990-01-01",
            telefono="70000001",
            motivo_consulta="Clínica Alpha",
        )
        Paciente.objects.create(
            clinica=self.clinica_b,
            nombre="Paciente Beta",
            ci="ISO-B01",
            fecha_nacimiento="1991-02-02",
            telefono="70000002",
            motivo_consulta="Clínica Beta",
        )
        self.login_url = reverse("api_login")

    def test_psicologo_solo_ve_sus_pacientes(self):
        """[SPRINT 1 - T024] [RF-29] Psicólogo Alpha NO ve pacientes de Beta."""
        resp = self.client.post(
            self.login_url, {"username": "psico_alpha", "password": "password123"}
        )
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + resp.data["access"])

        url = reverse("api_pacientes_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Solo debe ver pacientes de Clínica Alpha
        nombres = [p["nombre"] for p in response.data]
        self.assertIn("Paciente Alpha", nombres)
        self.assertNotIn("Paciente Beta", nombres)

    def test_dashboard_aislado_por_clinica(self):
        """[SPRINT 1 - T024] [RF-29] Dashboard devuelve datos solo del tenant."""
        resp = self.client.post(
            self.login_url, {"username": "psico_beta", "password": "password123"}
        )
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + resp.data["access"])

        url = reverse("api_dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["clinica"], "Clínica Beta")
        self.assertEqual(response.data["metricas"]["total_pacientes"], 1)


# ==============================================================================
# BLOQUE 7: TESTS DE GESTIÓN ADMINISTRATIVA [SPRINT 1 - T024]
# ==============================================================================
class ClinicaRegistroTests(APITestCase):
    """Valida el registro de nuevas clínicas/tenants (CU-25)."""

    def setUp(self):
        self.clinica = Clinica.objects.create(
            nombre="Clínica Admin",
            nit="ADMIN-001",
            direccion="Av. Admin 600",
        )
        self.admin = Usuario.objects.create_user(
            username="admin_clinicas",
            password="password123",
            clinica=self.clinica,
            rol="ADMIN",
        )
        self.login_url = reverse("api_login")

    def test_registrar_clinica_exitoso(self):
        """[SPRINT 1 - T024] [CU-25] Admin puede registrar un nuevo tenant."""
        resp = self.client.post(
            self.login_url,
            {"username": "admin_clinicas", "password": "password123"},
        )
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + resp.data["access"])

        data = {
            "nombre": "Clínica Nueva SaaS",
            "nit": "SAAS-001",
            "direccion": "Av. SaaS 700",
        }
        url = reverse("api_registrar_clinica")
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Clinica.objects.count(), 2)

    def test_registrar_clinica_nit_duplicado(self):
        """[SPRINT 1 - T024] NIT duplicado es rechazado por la BD."""
        resp = self.client.post(
            self.login_url,
            {"username": "admin_clinicas", "password": "password123"},
        )
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + resp.data["access"])

        data = {"nombre": "Otra Clínica", "nit": "ADMIN-001", "direccion": "Duplicada"}
        url = reverse("api_registrar_clinica")
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
