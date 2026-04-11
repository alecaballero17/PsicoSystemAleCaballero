# 📊 REPORTE SPRINT 0 — Correcciones y Saneamiento

**Proyecto:** PsicoSystem SI2  
**Fecha:** 2026-04-11  
**Sprint:** 0 (T001–T009)  
**Estado:** ✅ SANEADO

---

## Resumen de Correcciones

### 1. ✅ GitFlow (T003)
- **Problema:** Solo existían ramas `main` y `desarrollo-joelramos`, sin flujo GitFlow formal.
- **Solución:** Se crearon las ramas:
  - `dev` — Rama de integración.
  - `feature/mejoras-sprint0` — Rama de trabajo para las correcciones.
- **Flujo aplicado:** `feature → dev → main`.

### 2. ✅ Wireframes (T007)
- **Problema:** Existían las vistas finales pero no los prototipos de diseño previos.
- **Solución:** Se generaron 3 wireframes de alta fidelidad en `docs/design/wireframes/`:
  - `01_login.png` — Pantalla de autenticación.
  - `02_dashboard.png` — Dashboard administrativo SaaS.
  - `03_registro_paciente.png` — Formulario de registro de pacientes.

### 3. ✅ Definition of Done (T009)
- **Problema:** No existía un documento que defina los criterios de aceptación.
- **Solución:** Se creó `docs/DEFINITION_OF_DONE.md` con 6 categorías:
  1. Código Fuente (nomenclatura, trazabilidad).
  2. Seguridad (JWT, RBAC, input validation).
  3. Pruebas (cobertura ≥ 70%).
  4. Documentación (OpenAPI, docstrings).
  5. Control de Versiones (convención de commits).
  6. Revisión de Pares.

### 4. ✅ Cobertura de Tests (RNF-08)
- **Problema:** Solo 4 tests en backend y 3 superficiales en frontend.
- **Solución:** Se expandió `core/tests.py` de 4 a **26 tests automatizados**:

| Bloque | Tests | Cobertura |
| :--- | :---: | :--- |
| Modelos (T005) | 5 | Clinica, Usuario, Paciente, Cita, CI único |
| JWT Auth (T011) | 5 | Login ok, login fail, /me/ auth, /me/ 401 |
| Logout/Blacklist (T022) | 3 | Logout ok, sin refresh, doble logout |
| RBAC (T018) | 4 | Admin crea clínica, psicólogo denegado |
| Registro Pacientes (T014) | 5 | Crear, CI duplicado, listar, sin auth |
| Multi-tenant (T024) | 2 | Aislamiento entre clínicas |
| Admin Clínicas (CU-25) | 2 | Registro y NIT duplicado |

**Resultado:** `26 tests — OK ✅` (100% éxito).

---

## Estado Final Sprint 0

| Tarea | Estado Anterior | Estado Actual |
| :--- | :---: | :---: |
| T001 Arquitectura | ✅ | ✅ |
| T002 Stack | ✅ | ✅ |
| **T003 GitFlow** | ⚠️ PARCIAL | ✅ CUMPLE |
| T004 Entorno | ✅ | ✅ |
| T005 Modelado | ✅ | ✅ |
| T006 MVP | ✅ | ✅ |
| **T007 Wireframes** | ⚠️ PARCIAL | ✅ CUMPLE |
| T008 Conectividad | ✅ | ✅ |
| **T009 Estándares/DoD** | ⚠️ PARCIAL | ✅ CUMPLE |
| **RNF-08 Tests** | ⚠️ PARCIAL | ✅ CUMPLE |

**Sprint 0: 9/9 CUMPLE + 3/3 RNFs CUMPLE = 100% ✅**
