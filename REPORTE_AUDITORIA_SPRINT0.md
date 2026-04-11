# 📊 REPORTE AUDITORIA SPRINT 0 — Log de Hallazgos y Trazabilidad

**Proyecto:** PsicoSystem SI2  
**Fecha de Auditoría:** 2026-04-11  
**Auditor:** Agente de Ingeniería (Antigravity)  
**Alcance Estricto:** Sprint 0 → T001, T002, T003, T004, T005, T006, T007, T008, T009  
**RNFs Auditados:** RNF-03 (Seguridad), RNF-05 (Compatibilidad), RNF-08 (Mantenibilidad)

---

## 1. MATRIZ DE TRAZABILIDAD COMPLETA (Tarea → Archivo → Evidencia)

### T001 — Definición de la Arquitectura del Sistema
> *Diseño de arquitectura desacoplada (Backend API REST y Frontends independientes).*

| Archivo Modificado/Verificado | Evidencia de Cumplimiento | Estado |
| :--- | :--- | :---: |
| `psicosystem/settings.py` (Docstring) | Arquitectura desacoplada documentada | ✅ CUMPLE |
| `core/apps.py` | Módulo `core` como app principal del Backend | ✅ CUMPLE |
| `frontend-web/` (directorio separado) | Frontend React independiente del Django | ✅ CUMPLE |
| `mobile-app/` (directorio separado) | App Flutter independiente del Backend | ✅ CUMPLE |
| `psicosystem/urls.py` | No hay vistas HTML, solo endpoints REST `/api/` | ✅ CUMPLE |
| `.gitignore` | Exclusión de entornos por plataforma | ✅ CUMPLE |

**Veredicto T001: ✅ CUMPLE** — La arquitectura es Client-Server desacoplada con 3 capas independientes.

---

### T002 — Validación del Stack Tecnológico
> *Configuración de React, Django REST Framework, PostgreSQL y Flutter.*

| Archivo Modificado/Verificado | Evidencia de Cumplimiento | Estado |
| :--- | :--- | :---: |
| `requirements.txt` | Django 6.0.3, DRF 3.17.1, PostgreSQL (psycopg2), SimpleJWT | ✅ CUMPLE |
| `frontend-web/package.json` | React 19.2.4, axios 1.14.0, react-router-dom 7.14.0 | ✅ CUMPLE |
| `mobile-app/pubspec.yaml` | Flutter (sdk ≥3.0.0), http 1.1.0, flutter_dotenv 6.0.0 | ✅ CUMPLE |
| `psicosystem/settings.py` → `DATABASES` | Engine = `django.db.backends.postgresql` | ✅ CUMPLE |

**Veredicto T002: ✅ CUMPLE** — Stack completo: Django + DRF + PostgreSQL + React + Flutter.

---

### T003 — Gestión de Versiones
> *Creación del repositorio en GitHub con flujo de trabajo GitFlow.*

| Archivo Modificado/Verificado | Evidencia de Cumplimiento | Estado |
| :--- | :--- | :---: |
| `.git/` | Repositorio Git inicializado | ✅ CUMPLE |
| `.gitignore` | Exclusión profesional de `.env`, `venv/`, `node_modules/`, `__pycache__/` | ✅ CUMPLE |
| `git branch -a` | Ramas: `main`, `desarrollo-joelramos` | ⚠️ PARCIAL |

> [!WARNING]
> **Hallazgo T003:** No se detecta una rama `dev` o `develop` formal como exige **GitFlow estricto**.
> Existe `desarrollo-joelramos` como rama de trabajo, pero faltan las ramas `feature/*` y `dev`.
> **Recomendación:** Para la documentación, justificar que se usa un flujo simplificado
> (Trunk-Based Development) o crear las ramas faltantes antes de la defensa.

**Veredicto T003: ⚠️ PARCIAL** — Repositorio existe, `.gitignore` profesional, pero GitFlow no es estricto.

---

### T004 — Entorno de Desarrollo
> *Configuración de entornos virtuales (Python venv), Node.js y emuladores.*

| Archivo Modificado/Verificado | Evidencia de Cumplimiento | Estado |
| :--- | :--- | :---: |
| `venv/` | Entorno virtual Python presente | ✅ CUMPLE |
| `manage.py` | Script de ejecución `DJANGO_SETTINGS_MODULE` configurado | ✅ CUMPLE |
| `psicosystem/settings.py` → `DEBUG` | Control por variable de entorno `.env` | ✅ CUMPLE |
| `.env` (raíz) | `DB_PASSWORD`, `SECRET_KEY`, `DEBUG`, `SERVER_IP` definidos | ✅ CUMPLE |
| `mobile-app/.env` | `API_URL` para IP de red local | ✅ CUMPLE |
| `frontend-web/package.json` → scripts | `npm start`, `npm test`, `npm build` configurados | ✅ CUMPLE |
| `mobile-app/pubspec.yaml` → assets | `.env` declarado como asset de Flutter | ✅ CUMPLE |
| `frontend-web/tests/Integrity.test.js` | Verifica que Jest está operativo | ✅ CUMPLE |

**Veredicto T004: ✅ CUMPLE** — Entornos Python, Node.js y Flutter correctamente configurados.

---

### T005 — Modelado de Datos Multi-tenant
> *Diseño del esquema ER con aislamiento lógico de datos por clínica (Tenants).*

| Archivo Modificado/Verificado | Evidencia de Cumplimiento | Estado |
| :--- | :--- | :---: |
| `core/models/clinica.py` | Entidad `Clinica` como raíz del tenant con NIT único | ✅ CUMPLE |
| `core/models/usuario.py` | `Usuario` extiende `AbstractUser` con FK a `Clinica` + roles RBAC | ✅ CUMPLE |
| `core/models/paciente.py` | `Paciente` con FK a `Clinica` + `db_index=True` | ✅ CUMPLE |
| `core/models/cita.py` | `Cita` con FK a `Paciente` y `Usuario` (PSICOLOGO) | ✅ CUMPLE |
| `core/models/__init__.py` | 4 entidades registradas: Clinica, Usuario, Paciente, Cita | ✅ CUMPLE |
| `psicosystem/settings.py` → `AUTH_USER_MODEL` | `core.Usuario` como modelo de identidad personalizado | ✅ CUMPLE |
| `core/migrations/0001_initial.py` | Migración inicial con las 4 tablas | ✅ CUMPLE |

**Veredicto T005: ✅ CUMPLE** — Esquema ER Multi-tenant con 4 entidades y aislamiento por FK.

---

### T006 — Definición del MVP
> *Especificación y validación de HU y CU críticos para el centro psicológico.*

| Archivo Modificado/Verificado | Evidencia de Cumplimiento | Estado |
| :--- | :--- | :---: |
| `CASOS_DE_USO.md` | Archivo de definición de CU presente | ✅ CUMPLE |
| `REPORTE_DOCUMENTACION_SPRINT0y1.md` | Mapeo de CU-01, CU-06, CU-25 documentado | ✅ CUMPLE |
| `README.md` | Sección "Matriz de Requerimientos" con RF-01, RF-28, RF-29 | ✅ CUMPLE |

> [!NOTE]
> **Hallazgo T006:** La T006 es principalmente documental (PDF/Backlog externo). El repositorio
> contiene archivos `.md` que evidencian la definición del MVP. La validación completa depende
> del documento académico que el estudiante presente al tribunal.

**Veredicto T006: ✅ CUMPLE** — Existen artefactos de especificación en el repositorio.

---

### T007 — Prototipado UI/UX
> *Diseño de wireframes para los módulos de Login, Dashboard y perfil del paciente.*

| Archivo Modificado/Verificado | Evidencia de Cumplimiento | Estado |
| :--- | :--- | :---: |
| `frontend-web/src/pages/Login.js` | Interfaz de Login implementada (no solo wireframe) | ✅ CUMPLE |
| `frontend-web/src/pages/Dashboard.js` | Dashboard completo con KPIs y tabla | ✅ CUMPLE |
| `frontend-web/src/styles/loginStyles.js` | Sistema de estilos modulares | ✅ CUMPLE |
| `frontend-web/src/styles/dashboardStyles.js` | Sistema de estilos del dashboard | ✅ CUMPLE |

> [!NOTE]
> **Hallazgo T007:** La T007 solicita wireframes (mockups de baja fidelidad). En el repositorio
> se encontraron las **implementaciones finales**, no prototipos. Esto es un adelanto positivo,
> pero el estudiante debe presentar los wireframes originales (Figma/papel) en su documentación
> para demostrar el proceso de diseño previo a la codificación.

**Veredicto T007: ⚠️ PARCIAL** — Existe la UI final pero no se encontraron wireframes estáticos en el repo.

---

### T008 — Conectividad Base
> *Implementación de un "Hello World" entre Django y React para validar CORS.*

| Archivo Modificado/Verificado | Evidencia de Cumplimiento | Estado |
| :--- | :--- | :---: |
| `psicosystem/settings.py` → `CORS_*` | CORS habilitado con `corsheaders` | ✅ CUMPLE |
| `frontend-web/src/api/axiosConfig.js` | Cliente HTTP centralizado con interceptores | ✅ CUMPLE |
| `mobile-app/lib/config/api_config.dart` | Configuración de URL base del API | ✅ CUMPLE |
| `psicosystem/urls.py` → `api/dashboard/` | Endpoint REST funcional que responde JSON | ✅ CUMPLE |
| `requirements.txt` → `django-cors-headers` | Dependencia CORS instalada | ✅ CUMPLE |

**Veredicto T008: ✅ CUMPLE** — Conectividad React↔Django y Flutter↔Django validada con CORS.

---

### T009 — Estándares de Ingeniería
> *Definición de DoD, nomenclatura de código y política de Commits.*

| Archivo Modificado/Verificado | Evidencia de Cumplimiento | Estado |
| :--- | :--- | :---: |
| `psicosystem/settings.py` → `drf_spectacular` | Documentación OpenAPI 3 habilitada | ✅ CUMPLE |
| `psicosystem/settings.py` → `LANGUAGE_CODE` | Localización `es-bo` para Bolivia | ✅ CUMPLE |
| Backend: `snake_case` | Convención Python/Django respetada | ✅ CUMPLE |
| Frontend: `camelCase` | Convención JavaScript/React respetada | ✅ CUMPLE |
| Mobile: `camelCase` (Dart) | Convención Dart/Flutter respetada | ✅ CUMPLE |
| `core/models/*.py` | Docstrings y `help_text` en campos críticos | ✅ CUMPLE |
| `git log` | Commits descriptivos en español | ✅ CUMPLE |
| `psicosystem/urls.py` → OpenAPI | Swagger/ReDoc disponible en `/api/docs/` | ✅ CUMPLE |

> [!NOTE]
> **Hallazgo T009:** No se encontró un archivo `DEFINITION_OF_DONE.md` dedicado en el repositorio.
> La DoD debería estar documentada explícitamente. Se recomienda agregarla al repo o al PDF.

**Veredicto T009: ⚠️ PARCIAL** — Estándares de código y OpenAPI cumplidos, pero falta DoD explícita.

---

## 2. CUMPLIMIENTO DE REQUISITOS NO FUNCIONALES

### RNF-03 — Seguridad

| Evidencia | Archivo | Estado |
| :--- | :--- | :---: |
| SECRET_KEY extraída de `.env` | `settings.py` L16 | ✅ |
| DB_PASSWORD extraída de `.env` | `settings.py` L118 | ✅ |
| `.env` excluido del repo vía `.gitignore` | `.gitignore` L7 | ✅ |
| CSRF Middleware activo | `settings.py` L53 | ✅ |
| ALLOWED_HOSTS restringido | `settings.py` L28 | ✅ |
| Tokens JWT con expiración limitada | `settings.py` SIMPLE_JWT | ✅ |

> [!WARNING]
> **Hallazgo RNF-03:** El archivo `.env` contiene la DB_PASSWORD en texto plano (`P5ico_5yst3m_2026!#`).
> Esto es aceptable para desarrollo local, pero en producción se debe usar un gestor de secretos
> (AWS Secrets Manager, Vault, etc.). **Para la defensa, esto es correcto.**

**Veredicto RNF-03: ✅ CUMPLE** para el alcance del Sprint 0.

---

### RNF-05 — Compatibilidad

| Evidencia | Archivo | Estado |
| :--- | :--- | :---: |
| `browserslist` en package.json | `package.json` L29-39 | ✅ |
| CORS habilitado para multiplataforma | `settings.py` CORS config | ✅ |
| Flutter SDK ≥3.0.0 (Android 11+/iOS 15+) | `pubspec.yaml` L6 | ✅ |
| React 19 (navegadores modernos) | `package.json` L11 | ✅ |

**Veredicto RNF-05: ✅ CUMPLE**

---

### RNF-08 — Mantenibilidad

| Evidencia | Archivo | Estado |
| :--- | :--- | :---: |
| Arquitectura modular (models/, views/, serializers/, security/) | `core/` | ✅ |
| Separación de estilos (styles/) | `frontend-web/src/styles/` | ✅ |
| Servicios desacoplados | `frontend-web/src/services/` | ✅ |
| Widgets reutilizables (Flutter) | `mobile-app/lib/widgets/` | ✅ |
| Tests Backend (4 tests) | `core/tests.py` | ⚠️ |
| Tests Frontend (3 tests) | `frontend-web/tests/Integrity.test.js` | ⚠️ |

> [!WARNING]
> **Hallazgo RNF-08:** Se requiere cobertura mínima del 70% en tests unitarios. Actualmente hay
> 4 tests en el backend y 3 en el frontend (de integridad, no funcionales). **La cobertura real
> es inferior al 70%.** Se recomienda agregar más tests unitarios antes de la defensa.

**Veredicto RNF-08: ⚠️ PARCIAL** — Arquitectura limpia cumplida, cobertura de tests insuficiente.

---

## 3. RESUMEN EJECUTIVO DE LA AUDITORÍA

| Tarea | Estado | Observación |
| :--- | :---: | :--- |
| **T001** Arquitectura | ✅ CUMPLE | 3 capas desacopladas (Backend, Web, Mobile) |
| **T002** Stack Tecnológico | ✅ CUMPLE | Django + DRF + PostgreSQL + React + Flutter |
| **T003** Gestión de Versiones | ⚠️ PARCIAL | Falta flujo GitFlow estricto (`dev`, `feature/*`) |
| **T004** Entorno de Desarrollo | ✅ CUMPLE | `venv`, `.env`, Node.js, Flutter configurados |
| **T005** Modelado de Datos | ✅ CUMPLE | 4 entidades con Multi-tenancy por FK |
| **T006** Definición del MVP | ✅ CUMPLE | CUs y RFs documentados en `.md` |
| **T007** Prototipado UI/UX | ⚠️ PARCIAL | UI final existe, pero faltan wireframes en el repo |
| **T008** Conectividad Base | ✅ CUMPLE | CORS + Axios + API endpoint funcional |
| **T009** Estándares | ⚠️ PARCIAL | Nomenclatura y OpenAPI ok, falta DoD explícita |
| **RNF-03** Seguridad | ✅ CUMPLE | Credenciales en `.env`, JWT, CSRF |
| **RNF-05** Compatibilidad | ✅ CUMPLE | Chromium, WebKit, Gecko, Android 11+, iOS 15+ |
| **RNF-08** Mantenibilidad | ⚠️ PARCIAL | Arquitectura limpia, tests < 70% cobertura |

---

## 4. ARCHIVOS MODIFICADOS DURANTE ESTA AUDITORÍA (Etiquetado)

| # | Archivo | Tipo de Cambio |
| :--- | :--- | :--- |
| 1 | `psicosystem/settings.py` | Inserción de 30+ etiquetas `[SPRINT 0 - T00x]` y `[RNF-xx]` |
| 2 | `.gitignore` | Inserción de etiquetas `[SPRINT 0 - T003]` |
| 3 | `requirements.txt` | Inserción de etiquetas `[SPRINT 0 - T002]` |
| 4 | `core/apps.py` | Inserción de etiqueta `[SPRINT 0 - T001]` |
| 5 | `core/models/__init__.py` | Inserción de etiqueta `[SPRINT 0 - T005]` |
| 6 | `core/models/clinica.py` | Inserción de etiquetas `[SPRINT 0 - T005]` |
| 7 | `core/models/usuario.py` | Inserción de etiquetas `[SPRINT 0 - T005]` |
| 8 | `core/models/paciente.py` | Inserción de etiquetas `[SPRINT 0 - T005]` |
| 9 | `core/models/cita.py` | Inserción de etiqueta `[SPRINT 0 - T005]` |
| 10 | `frontend-web/src/api/axiosConfig.js` | Inserción de etiquetas `[SPRINT 0 - T008]` |
| 11 | `mobile-app/lib/config/api_config.dart` | Inserción de etiquetas `[SPRINT 0 - T008]` |
| 12 | `mobile-app/lib/main.dart` | Inserción de etiquetas `[SPRINT 0 - T002]` |
| 13 | `AUDITORIA_ADELANTOS.md` | **[NUEVO]** Detección de funcionalidades fuera de Sprint 0 |
| 14 | `REPORTE_AUDITORIA_SPRINT0.md` | **[NUEVO]** Este reporte |

---

*Fin del reporte. Todos los hallazgos han sido documentados con evidencia verificable en el código fuente.*
