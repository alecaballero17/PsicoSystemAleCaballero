# 📊 REPORTE SPRINT 1 — Implementación y Trazabilidad

**Proyecto:** PsicoSystem SI2  
**Fecha:** 2026-04-11  
**Sprint:** 1 (T010–T026)  
**Estado:** ✅ IMPLEMENTADO

---

## Matriz de Trazabilidad Sprint 1

### Tareas Implementadas

| Tarea | Descripción | Archivos Clave | RF/CU | Estado |
| :--- | :--- | :--- | :--- | :---: |
| **T010** | Interfaz Login Web | `pages/Login.js`, `styles/loginStyles.js` | RF-01, CU-01 | ✅ |
| **T011** | Core JWT Backend | `auth_views.py`, `jwt_serializers.py` | RF-01, CU-01 | ✅ |
| **T012** | Auth Flutter | `login_screen.dart`, `auth_service.dart` | RF-01, CU-01 | ✅ |
| **T013** | Registro Pacientes Web | `pages/RegistroPaciente.js` | RF-02, CU-02 | ✅ |
| **T014** | Endpoints Pacientes | `paciente_views.py`, `paciente_serializer.py` | RF-02, CU-02 | ✅ |
| **T015** | Onboarding Móvil | `paciente_dashboard_screen.dart` | RF-02, CU-02 | ✅ |
| **T016** | Dashboard Psicólogos | `pages/Dashboard.js`, `dashboard_views.py` | RF-04 | ✅ |
| **T017** | CRUD Psicólogos API | `clinica_views.py` → `UsuarioCreateAPIView` | RF-04, RF-28 | ✅ |
| **T018** | Middleware RBAC | `permissions.py` (IsAdmin, IsPsicologo) | RF-28 | ✅ |
| **T019** | Recuperación Contraseña | `password_reset_views.py` | CU-03 | ✅ |
| **T020** | Módulo SMTP | `settings.py` EMAIL_BACKEND config | CU-03 | ✅ |
| **T021** | Logout React | `AuthContext.js` → `logout()` | CU-04 | ✅ |
| **T022** | Blacklist JWT | `auth_views.py` → `LogoutAPIView` | CU-04 | ✅ |
| **T023** | Logging y Auditoría | `audit_middleware.py`, `settings.py` LOGGING | RF-30 | ✅ |
| **T024** | Registro Clínica | `clinica_views.py` → `ClinicaCreateAPIView` | RF-29, CU-25 | ✅ |
| **T025** | Suscripciones SaaS | `models/suscripcion.py` (PlanSuscripcion, Suscripcion) | CU-24 | ✅ |
| **T026** | Seguridad Avanzada | `settings.py` hardening (XSS, HSTS, HTTPS) | RNF-03 | ✅ |

**Sprint 1: 17/17 Tareas Implementadas = 100% ✅**

---

## Requisitos Funcionales Cubiertos

| RF | Descripción | Implementación | Estado |
| :--- | :--- | :--- | :---: |
| RF-01 | Autenticación JWT | `SimpleJWT` + `CustomTokenObtainPairSerializer` | ✅ |
| RF-02 | Registro Pacientes | `PacienteCreateAPIView` + serializer + frontend | ✅ |
| RF-03 | Gestión de Perfiles | `MeAPIView` con datos del usuario autenticado | ✅ |
| RF-04 | Gestión Psicólogos | `UsuarioCreateAPIView` con FK a clínica | ✅ |
| RF-28 | RBAC | `IsAdmin`, `IsPsicologo` permission classes | ✅ |
| RF-29 | Aislamiento SaaS | FK obligatoria a Clínica en todos los modelos | ✅ |
| RF-30 | Registro de Auditoría | `AuditLogMiddleware` + LOGGING config | ✅ |

---

## Casos de Uso Cubiertos

| CU | Descripción | Endpoints | Estado |
| :--- | :--- | :--- | :---: |
| CU-01 | Autenticación JWT | `POST /api/auth/login/` | ✅ |
| CU-02 | Registro Paciente | `POST /api/pacientes/registrar/` | ✅ |
| CU-03 | Recuperación Credenciales | `POST /api/auth/password-reset/` | ✅ |
| CU-04 | Terminación Sesión | `POST /api/auth/logout/` | ✅ |
| CU-05 | Gestión Psicólogos | `POST /api/usuarios/` (rol=PSICOLOGO) | ✅ |
| CU-24 | Suscripciones SaaS | Modelo `PlanSuscripcion` + `Suscripcion` | ✅ |
| CU-25 | Registro Clínicas | `POST /api/clinicas/` | ✅ |

---

## RNFs Validados

| RNF | Evidencia | Estado |
| :--- | :--- | :---: |
| RNF-03 | Security hardening condicional (HSTS, XSS, HTTPS, cookies seguras) | ✅ |
| RNF-06 | Arquitectura stateless (JWT) permite escalabilidad horizontal | ✅ |

---

## Endpoints de la API (Sprint 1)

```
POST   /api/auth/login/                    → JWT Login (T011)
POST   /api/auth/refresh/                  → Token Refresh (T011)
POST   /api/auth/logout/                   → Blacklist Logout (T022)
GET    /api/auth/me/                        → Perfil usuario (T011)
POST   /api/auth/password-reset/            → Solicitar reset (T019/T020)
POST   /api/auth/password-reset/confirm/    → Confirmar reset (T019/T020)
POST   /api/clinicas/                       → Registrar clínica (T024)
POST   /api/usuarios/                       → Registrar usuario (T017)
GET    /api/dashboard/                      → Métricas (T016)
GET    /api/pacientes/                      → Listar pacientes (T014)
POST   /api/pacientes/registrar/            → Registrar paciente (T014)
GET    /api/schema/                         → OpenAPI Schema (T009)
GET    /api/docs/swagger/                   → Swagger UI (T009)
GET    /api/docs/redoc/                     → ReDoc (T009)
```

---

## Verificación Automatizada

```
$ python manage.py test core -v 2
----------------------------------------------------------------------
Ran 26 tests in 45.535s

OK ✅
```

---

## Archivos Nuevos Creados en Sprint 1

| # | Archivo | Tarea |
| :--- | :--- | :--- |
| 1 | `core/security/audit_middleware.py` | T023 |
| 2 | `core/security/password_reset_views.py` | T019, T020 |
| 3 | `core/models/suscripcion.py` | T025 |
| 4 | `core/migrations/0005_add_suscripcion_saas_t025.py` | T025 |
| 5 | `docs/DEFINITION_OF_DONE.md` | T009 |
| 6 | `docs/design/wireframes/01_login.png` | T007 |
| 7 | `docs/design/wireframes/02_dashboard.png` | T007 |
| 8 | `docs/design/wireframes/03_registro_paciente.png` | T007 |

---

*Reporte generado y validado con 26 tests automatizados exitosos.*
