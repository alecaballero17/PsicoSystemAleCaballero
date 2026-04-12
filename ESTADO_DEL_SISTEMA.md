# ESTADO DEL SISTEMA — PsicoSystem SI2
### Reporte de Auditoría de Trazabilidad v1.0.5
**Fecha:** 2026-04-12 | **Ejecutado por:** Script Interno de Auditoría y Aseguramiento de Calidad

---

## 1. INVENTARIO DE SPRINT 0 (T001–T009)

| Tarea | Descripción | Estado | Archivos Clave |
|-------|-------------|--------|----------------|
| **T001** | Arquitectura desacoplada (Backend REST + Frontends independientes) | ✅ CUMPLIDO | `psicosystem/settings.py`, `psicosystem/urls.py` |
| **T002** | Stack Tecnológico: Django 6.0.3 + DRF 3.17.1 + PostgreSQL + React 19 + Flutter | ✅ CUMPLIDO | `requirements.txt`, `package.json`, `pubspec.yaml` |
| **T003** | GitFlow (main, dev, feature) | ✅ CUMPLIDO | `.git/`, `.gitignore` |
| **T004** | Entorno de desarrollo: Python venv, Node.js, Android SDK | ✅ CUMPLIDO | `psicosystem/settings.py` (decouple/.env) |
| **T005** | Modelado Multi-tenant (ER con aislamiento por clínica) | ✅ CUMPLIDO | `core/models/clinica.py`, `usuario.py`, `paciente.py`, `cita.py` |
| **T006** | Definición del MVP (historias de usuario y CU) | ✅ CUMPLIDO | Documentación externa (Jira/Notion) |
| **T007** | Prototipado UI/UX (Login, Dashboard, Perfil Paciente) | ✅ CUMPLIDO | `frontend-web/src/pages/Login.js`, `Dashboard.js` |
| **T008** | Conectividad Base (Django ↔ React, CORS) | ✅ CUMPLIDO | `frontend-web/src/api/axiosConfig.js`, `settings.py` (CORS) |
| **T009** | Estándares de Ingeniería (DoD, nomenclatura, commits) | ✅ CUMPLIDO | Comentarios de trazabilidad en todo el código, `drf-spectacular` |

### RNF Sprint 0

| RNF | Descripción | Estado | Evidencia |
|-----|-------------|--------|-----------|
| **RNF-03** | Seguridad: cifrado, HTTPS/TLS, autenticación robusta | ✅ CUMPLIDO | JWT (SimpleJWT), SECRET_KEY vía `.env`, password hashing (PBKDF2) |
| **RNF-05** | Compatibilidad: Chromium/WebKit/Gecko + Android 11+/iOS 15+ | ✅ CUMPLIDO | React SPA compatible, Flutter multi-plataforma |
| **RNF-08** | Mantenibilidad: estándares y arquitectura limpia | ⚠️ PARCIAL | Clean Architecture aplicada; cobertura de tests unitarios < 70% |

---

## 2. INVENTARIO DE SPRINT 1 (T010–T026)

### Tareas Web

| Tarea | Descripción | Estado | Archivos |
|-------|-------------|--------|----------|
| **T010** | Interfaz de Autenticación (Login React) | ✅ CUMPLIDO | `pages/Login.js`, `styles/loginStyles.js` |
| **T011** | Core de Seguridad JWT (SimpleJWT) | ✅ CUMPLIDO | `security/jwt_serializers.py`, `security/auth_views.py` |
| **T013** | Módulo de Registro de Pacientes (UI Web) | ✅ CUMPLIDO | `pages/RegistroPaciente.js`, `pages/Dashboard.js` (tabla) |
| **T016** | Dashboard de Gestión de Personal | ✅ CUMPLIDO | `pages/GestionPersonal.js` |
| **T019** | Flujo de Recuperación de Credenciales (UI) | ✅ CUMPLIDO | `pages/RecuperarContrasena.js` |
| **T021** | Terminación de Sesión (Logout + Limpieza) | ✅ CUMPLIDO | `components/Navbar.js`, `services/authService.js` |

### Tareas Backend

| Tarea | Descripción | Estado | Archivos |
|-------|-------------|--------|----------|
| **T014** | Endpoints CRUD de Pacientes | ✅ CUMPLIDO | `views/paciente_views.py`, `serializers/paciente_serializer.py` |
| **T017** | CRUD de Psicólogos (vinculación Tenant) | ✅ CUMPLIDO | `views/clinica_views.py` (UsuarioListCreate/Detail) |
| **T018** | Middleware RBAC | ✅ CUMPLIDO | `security/permissions.py` (IsAdmin, IsPsicologo) |
| **T020** | Módulo SMTP (recuperación de contraseña) | ✅ CUMPLIDO | `security/password_reset_views.py`, `settings.py` (EMAIL_*) |
| **T022** | Blacklisting de Tokens (Logout server-side) | ✅ CUMPLIDO | `security/auth_views.py` (LogoutAPIView), `token_blacklist` app |
| **T023** | Logging y Auditoría | ✅ CUMPLIDO | `security/audit_middleware.py`, `settings.py` (LOGGING), `logs/audit.log` |
| **T024** | Registro de Clínica (Tenant) | ✅ CUMPLIDO | `views/clinica_views.py` (ClinicaCreateAPIView) |
| **T025** | Gestión de Suscripciones SaaS | ✅ CUMPLIDO | `views/suscripcion_views.py`, `models/suscripcion.py` |
| **T026** | Seguridad Avanzada (hardening) | ✅ CUMPLIDO | `settings.py` líneas 252-261 (HSTS, XSS Filter, CSRF Secure) |

### Tareas Móvil (Flutter)

| Tarea | Descripción | Estado | Archivos |
|-------|-------------|--------|----------|
| **T012** | Consumo de Auth API (Flutter) | ✅ CUMPLIDO | `mobile-app/lib/services/auth_service.dart` |
| **T015** | Onboarding Móvil (Registro Paciente) | ✅ CUMPLIDO | `mobile-app/lib/screens/`, `pages/RegistroPacientePublico.js` (endpoint) |

### Requisitos Funcionales Sprint 1

| RF | Descripción | Estado | Evidencia |
|----|-------------|--------|-----------|
| **RF-01** | Autenticación Stateless (JWT) | ✅ CUMPLIDO | SimpleJWT con access/refresh tokens |
| **RF-02** | Registro de Pacientes | ✅ CUMPLIDO | `PacienteCreateAPIView`, `PacienteRegistroPublicoAPIView` |
| **RF-03** | Gestión de Perfiles | ✅ CUMPLIDO | `MeAPIView`, `ClinicaConfigAPIView` |
| **RF-04** | Gestión de Psicólogos | ✅ CUMPLIDO | `UsuarioListCreateAPIView`, `UsuarioDetailAPIView` |
| **RF-28** | Control de Acceso RBAC | ✅ CUMPLIDO | `permissions.py`, `PrivateRoute` en React, `allowedRoles` |
| **RF-29** | Aislamiento SaaS (Multi-tenant) | ✅ CUMPLIDO | Filtro `clinica=request.user.clinica` en todas las vistas |
| **RF-30** | Registro de Auditoría | ✅ CUMPLIDO | `AuditLogMiddleware`, `logs/audit.log`, Soft Delete con log |

### Casos de Uso Sprint 1

| CU | Descripción | Estado | Evidencia |
|----|-------------|--------|-----------|
| **CU-01** | Autenticación de Usuario (JWT) | ✅ CUMPLIDO | `CustomTokenObtainPairView` + Login.js |
| **CU-02** | Registro de Paciente (Onboarding) | ✅ CUMPLIDO | `PacienteCreateAPIView` + RegistroPaciente.js |
| **CU-03** | Recuperación de Credenciales | ✅ CUMPLIDO | `PasswordResetRequestAPIView` + RecuperarContrasena.js |
| **CU-04** | Terminación de Sesión (Logout) | ✅ CUMPLIDO | `LogoutAPIView` + Navbar.js (botón Logout) |
| **CU-05** | Gestión de Perfiles de Psicólogos | ✅ CUMPLIDO | `UsuarioListCreateAPIView` + GestionPersonal.js |
| **CU-24** | Gestión de Planes y Suscripciones SaaS | ✅ CUMPLIDO | `PlanListAPIView` + `SuscripcionClinicaAPIView` + SuscripcionInfo.js |
| **CU-25** | Registro de Nuevas Clínicas (Tenants) | ✅ CUMPLIDO | `ClinicaCreateAPIView` + RegistroClinica.js |

---

## 3. MAPA DE RUTAS DEL SISTEMA

### Rutas Frontend (React — localhost:3000)

| Ruta | Componente | Acceso | Sprint |
|------|-----------|--------|--------|
| `/` | Landing.js | Público | Sprint 1 |
| `/login` | Login.js | Público | Sprint 1 (T010) |
| `/recuperar` | RecuperarContrasena.js | Público | Sprint 1 (T019/CU-03) |
| `/registro-clinica` | RegistroClinica.js | Público | Sprint 1 (T024/CU-25) |
| `/dashboard` | Dashboard.js | Todos los roles autenticados | Sprint 1 (T016) |
| `/registro-paciente` | RegistroPaciente.js | Solo PSICOLOGO | Sprint 1 (T013/CU-02) |
| `/gestion-personal` | GestionPersonal.js | Solo ADMIN | Sprint 1 (CU-05/T017) |
| `/configuracion-clinica` | ConfiguracionClinica.js | Solo ADMIN | Sprint 1 (T024/RF-29) |
| `/suscripcion` | SuscripcionInfo.js | Solo ADMIN | Sprint 1 (T025/CU-24) |

### Rutas Backend API (Django — localhost:8000)

| Ruta | Vista | Método | Sprint | Acceso |
|------|-------|--------|--------|--------|
| `/admin/` | Django Admin | GET | Sprint 0 | SuperUser |
| `/api/auth/login/` | CustomTokenObtainPairView | POST | Sprint 1 (T011) | Público |
| `/api/auth/refresh/` | TokenRefreshView | POST | Sprint 1 (T011) | Público |
| `/api/auth/logout/` | LogoutAPIView | POST | Sprint 1 (T022) | Autenticado |
| `/api/auth/me/` | MeAPIView | GET | Sprint 1 (RF-03) | Autenticado |
| `/api/auth/password-reset/` | PasswordResetRequestAPIView | POST | Sprint 1 (T019/T020) | Público |
| `/api/auth/password-reset/confirm/` | PasswordResetConfirmAPIView | POST | Sprint 1 (T019/T020) | Público |
| `/api/clinicas/` | ClinicaCreateAPIView | GET/POST | Sprint 1 (T024/CU-25) | Público |
| `/api/clinica/me/` | ClinicaConfigAPIView | GET/PUT | Sprint 1 (RF-29) | ADMIN |
| `/api/usuarios/` | UsuarioListCreateAPIView | GET/POST | Sprint 1 (T017/CU-05) | ADMIN |
| `/api/usuarios/<id>/` | UsuarioDetailAPIView | GET/PUT/DELETE | Sprint 1 (T017) | ADMIN |
| `/api/dashboard/` | DashboardAPIView | GET | Sprint 1 (T016) | Autenticado |
| `/api/pacientes/` | PacienteListAPIView | GET | Sprint 1 (T014) | PSICOLOGO |
| `/api/pacientes/registrar/` | PacienteCreateAPIView | POST | Sprint 1 (T014/CU-02) | PSICOLOGO |
| `/api/pacientes/<id>/` | PacienteDeleteAPIView | DELETE | Sprint 1 (RF-30) | ADMIN |
| `/api/pacientes/registro-publico/` | PacienteRegistroPublicoAPIView | POST | Sprint 1 (T015) | Público |
| `/api/pacientes/me/associate_clinic/` | AssociateClinicAPIView | POST | Sprint 1 (RF-29) | Autenticado |
| `/api/planes/` | PlanListAPIView | GET/POST | Sprint 1 (T025/CU-24) | Público(GET)/ADMIN(POST) |
| `/api/suscripciones/<clinica_id>/` | SuscripcionClinicaAPIView | GET/PUT | Sprint 1 (T025) | ADMIN |
| `/api/suscripciones/<clinica_id>/limites/` | LimitesClinicaAPIView | GET | Sprint 1 (T025) | ADMIN |
| `/api/schema/` | SpectacularAPIView | GET | Sprint 0 (T009) | Público |
| `/api/docs/swagger/` | SpectacularSwaggerView | GET | Sprint 0 (T009) | Público |
| `/api/docs/redoc/` | SpectacularRedocView | GET | Sprint 0 (T009) | Público |

---

## 4. MAPEO DE ADELANTOS DE ALCANCE POSTERIOR

### Modelos

| Modelo | Estado | Justificación |
|--------|--------|---------------|
| `Cita` (core/models/cita.py) | ✅ PRESERVADO (Sin endpoints) | Forma parte del esquema ER del Sprint 0 (T005). No tiene vistas, serializers ni rutas activas. La lógica de negocio es Sprint 2+. |

### Funcionalidades de Alcance Posterior Detectadas

| Funcionalidad | Estado | Nota |
|---------------|--------|------|
| Borrado Seguro (Soft Delete) de Pacientes | ✅ ACTIVO — Sprint 1 | Alineado con RF-30 (Auditoría) y RF-28 (RBAC: Solo ADMIN). El campo `activo` y `PacienteDeleteAPIView` cumplen trazabilidad. |
| Módulo de Citas (CRUD, Agenda) | 🔒 NO IMPLEMENTADO | Solo existe el modelo de datos (T005). Sin endpoints ni UI. Sprint 2+. |

> **Nota:** No se detectaron módulos fuera del alcance de Sprint 0/1 que requieran aislamiento. Todas las funcionalidades tienen trazabilidad directa a los requisitos oficiales.

---

## 5. ANÁLISIS DE VACÍOS (GAPS)

| ID | Descripción | Severidad | Recomendación |
|----|-------------|-----------|---------------|
| GAP-01 | **RNF-08**: Cobertura de tests < 70% | ⚠️ Media | Implementar tests unitarios con `pytest-django` para vistas y serializers críticos |
| GAP-02 | **RNF-06**: No se ha realizado prueba de carga formal (500 usuarios concurrentes) | ⚠️ Media | Ejecutar benchmark con `locust` o `ab` previo a la defensa |
| GAP-03 | **HTTPS/TLS**: Solo activo cuando `DEBUG=False` (producción) | ℹ️ Baja | Correcto para desarrollo. Documentar que en producción se activan las directivas de `settings.py` líneas 252-261 |

---

## 6. CREDENCIALES DE PRUEBA

| Usuario | Contraseña | Rol | Clínica |
|---------|-----------|-----|---------|
| `administrador` | `admin123` | ADMIN | Centro Psicológico UAGRM |
| `psicologo_uagrm` | (credencial original) | PSICOLOGO | Centro Psicológico UAGRM |

---

## 7. STACK TECNOLÓGICO CONFIRMADO

| Capa | Tecnología | Versión |
|------|-----------|---------|
| Backend | Django + DRF | 6.0.3 / 3.17.1 |
| Base de Datos | PostgreSQL | 16.x |
| Autenticación | SimpleJWT | 5.x |
| Frontend Web | React | 19.x |
| Frontend Móvil | Flutter/Dart | 3.x |
| Documentación API | drf-spectacular (OpenAPI 3) | 0.28.x |

---

*Reporte generado por el Script Interno de Auditoría y Aseguramiento de Calidad de PsicoSystem SI2.*
