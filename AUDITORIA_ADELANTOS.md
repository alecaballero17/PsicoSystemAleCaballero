# 🚨 AUDITORIA_ADELANTOS.md — Detección de Funcionalidades Fuera de Sprint 0

**Proyecto:** PsicoSystem SI2  
**Fecha de Auditoría:** 2026-04-11  
**Auditor:** Agente de Ingeniería (Antigravity)  
**Alcance:** Sprint 0 (T001–T009)

---

## Instrucción

Según la directiva de auditoría, cualquier funcionalidad, lógica o componente que pertenezca
a **Sprints posteriores al Sprint 0** debe ser catalogada aquí. Estos elementos **NO** fueron
etiquetados con `[SPRINT 0 - T00x]` porque no corresponden a las tareas T001–T009.

---

## 1. 🔐 Módulo de Autenticación JWT Completo (Sprint 1 — T010, T011, T012)

Estos archivos implementan Login/Logout con JWT, lo cual corresponde al **Sprint 1**.

| Archivo | Componente | Sprint Real |
| :--- | :--- | :--- |
| `core/security/auth_views.py` | `CustomTokenObtainPairView`, `LogoutAPIView`, `MeAPIView` | Sprint 1 (T011) |
| `core/security/jwt_serializers.py` | `CustomTokenObtainPairSerializer` (inyección de rol y clínica) | Sprint 1 (T011) |
| `core/security/permissions.py` | `IsAdmin`, `IsPsicologo` (RBAC) | Sprint 1 (T011) |
| `frontend-web/src/pages/Login.js` | Interfaz de Login Web con JWT | Sprint 1 (T010) |
| `frontend-web/src/services/authService.js` | Servicio de login, logout y getCurrentUser | Sprint 1 (T010, T011) |
| `frontend-web/src/context/AuthContext.js` | Estado global de autenticación (React Context) | Sprint 1 (T010) |
| `mobile-app/lib/screens/login_screen.dart` | Pantalla de Login Flutter | Sprint 1 (T012) |
| `mobile-app/lib/services/auth_service.dart` | Login y getCurrentUser móvil (HTTP+JWT) | Sprint 1 (T012) |
| `mobile-app/lib/models/auth_response_model.dart` | Modelo tipado de respuesta JWT | Sprint 1 (T012) |
| `psicosystem/settings.py` → `INSTALLED_APPS` | `rest_framework_simplejwt` y `token_blacklist` | Sprint 1 (T011) |
| `psicosystem/settings.py` → `SIMPLE_JWT` | Configuración de lifetime de tokens | Sprint 1 (T011) |
| `psicosystem/settings.py` → `REST_FRAMEWORK` | `JWTAuthentication` como autenticación por defecto | Sprint 1 (T011) |

---

## 2. 📋 Módulo de Registro de Pacientes (Sprint 1 — T013, T014)

La creación y listado de pacientes vía API REST corresponde al **Sprint 1**.

| Archivo | Componente | Sprint Real |
| :--- | :--- | :--- |
| `core/views/paciente_views.py` | `PacienteListAPIView`, `PacienteCreateAPIView` | Sprint 1 (T014) |
| `core/serializers/paciente_serializer.py` | `PacienteSerializer` | Sprint 1 (T014) |
| `frontend-web/src/pages/RegistroPaciente.js` | Formulario de registro web | Sprint 1 (T013) |
| `frontend-web/src/services/pacienteService.js` | Servicio de CRUD pacientes | Sprint 1 (T013, T014) |
| `mobile-app/lib/models/paciente_model.dart` | Modelo tipado de Paciente (Flutter) | Sprint 1 (T014) |
| `mobile-app/lib/services/auth_service.dart` → `getPacientes()` | Listado de pacientes desde móvil | Sprint 1 (T014) |

---

## 3. 📊 Dashboard Operativo (Sprint 1+)

| Archivo | Componente | Sprint Real |
| :--- | :--- | :--- |
| `core/views/dashboard_views.py` | `DashboardAPIView` (métricas por clínica) | Sprint 1+ |
| `frontend-web/src/pages/Dashboard.js` | Dashboard completo con tabla y KPIs | Sprint 1+ |
| `frontend-web/src/services/dashboardService.js` | Servicio de métricas | Sprint 1+ |
| `frontend-web/src/styles/dashboardStyles.js` | Estilos del dashboard | Sprint 1+ |
| `mobile-app/lib/screens/paciente_dashboard_screen.dart` | Dashboard del paciente (Flutter) | Sprint 1+ |

---

## 4. 🏥 Módulo de Registro de Clínicas y Usuarios vía API (Sprint 2+)

| Archivo | Componente | Sprint Real |
| :--- | :--- | :--- |
| `core/views/clinica_views.py` | `ClinicaCreateAPIView`, `UsuarioCreateAPIView` | Sprint 2+ |
| `core/serializers/clinica_serializer.py` | `ClinicaSerializer` | Sprint 2+ |
| `core/serializers/usuario_serializer.py` | `UsuarioSerializer` | Sprint 2+ |
| `frontend-web/src/pages/RegistroClinica.js` | Formulario de alta de clínica | Sprint 2+ |
| `frontend-web/src/services/clinicaService.js` | Servicio de registro de clínica | Sprint 2+ |

---

## 5. 🔬 Serializer de Citas (Sprint 2+)

| Archivo | Componente | Sprint Real |
| :--- | :--- | :--- |
| `core/serializers/cita_serializer.py` | `CitaSerializer` | Sprint 2+ (Agenda) |

---

## 6. 🧪 Tests de Integración (Sprint 1+)

| Archivo | Componente | Sprint Real |
| :--- | :--- | :--- |
| `core/tests.py` | Tests de JWT Login, Registro Paciente, Dashboard, RBAC | Sprint 1+ |
| `frontend-web/tests/Integrity.test.js` | Test de integridad del entorno Jest | Sprint 0 (T004) ✅ |

> **Nota:** El test `Integrity.test.js` **sí** corresponde al Sprint 0 porque valida que el entorno de testing esté configurado (T004).

---

## 7. 🐍 Script Simulador Flutter (Sprint 1)

| Archivo | Componente | Sprint Real |
| :--- | :--- | :--- |
| `scripts/simulador_flutter.py` | Simulación de peticiones HTTP desde Flutter | Sprint 1 (T012) |

---

## 8. 🧭 Componentes UI Globales (Sprint 1+)

| Archivo | Componente | Sprint Real |
| :--- | :--- | :--- |
| `frontend-web/src/components/Navbar.js` | Barra de navegación global con sesión | Sprint 1+ |
| `frontend-web/src/styles/loginStyles.js` | Estilos del Login | Sprint 1 (T010) |
| `frontend-web/src/styles/registroStyles.js` | Estilos del formulario de registro | Sprint 1 (T013) |
| `mobile-app/lib/widgets/custom_button.dart` | Botón reutilizable Flutter | Sprint 1 (T012) |
| `mobile-app/lib/widgets/custom_input.dart` | Input reutilizable Flutter | Sprint 1 (T012) |
| `mobile-app/lib/models/user_model.dart` | Modelo de usuario Flutter | Sprint 1 (T012) |

---

## Resumen Ejecutivo

| Sprint | Cantidad de Archivos Adelantados |
| :--- | :--- |
| **Sprint 1** (T010–T014) | ~28 archivos/componentes |
| **Sprint 2+** (Clínicas, Citas) | ~6 archivos/componentes |

> **Conclusión:** El repositorio tiene la base fundacional del Sprint 0 correctamente implementada,
> pero contiene un adelanto significativo del Sprint 1, lo cual es esperable en un proceso de desarrollo
> iterativo e incremental. No se detectaron funcionalidades inventadas fuera de los requerimientos definidos.
