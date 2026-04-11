# 🚨 AUDITORIA_ADELANTOS.md — Código Fuera de Sprint 0 y Sprint 1

**Proyecto:** PsicoSystem SI2  
**Última Actualización:** 2026-04-11  
**Alcance Auditado:** Sprint 0 (T001–T009) + Sprint 1 (T010–T026)

---

## Instrucciones de Aislamiento

Según la directiva de auditoría, el código que pertenece a **Sprints futuros (2+)**
debe ser catalogado aquí. Este código **NO se borra**, pero se documenta para que
el tribunal sepa que es trabajo planificado para iteraciones futuras.

---

## Módulos Adelantados (Sprint 2+)

### 1. Serializer de Citas (Sprint 2 — Módulo de Agenda)

| Archivo | Componente | Sprint Real | Status |
| :--- | :--- | :--- | :--- |
| `core/serializers/cita_serializer.py` | `CitaSerializer` | Sprint 2 (Agenda) | Registrado, no activo |
| `core/models/cita.py` | Modelo `Cita` | Sprint 0 (T005 Esquema BD) + Sprint 2 (Lógica) | Modelo presente, lógica futura |

> [!NOTE]
> El **modelo** `Cita` fue creado en el Sprint 0 como parte del diseño de BD (T005), 
> pero los endpoints CRUD y la lógica de agenda corresponden al Sprint 2.

### 2. Frontend — Componentes UI Futuros

| Archivo | Componente | Sprint Real |
| :--- | :--- | :--- |
| `frontend-web/src/pages/RegistroClinica.js` | Formulario de alta de clínica | Sprint 2+ (UI admin avanzado) |
| `frontend-web/src/services/clinicaService.js` | Servicio de API para clínicas | Sprint 2+ (UI admin avanzado) |

### 3. Mobile — Dashboard Paciente (Completitud pendiente)

| Archivo | Componente | Sprint Real |
| :--- | :--- | :--- |
| `mobile-app/lib/screens/paciente_dashboard_screen.dart` | Dashboard del paciente | Sprint 1 (T015) ✅ implementado |

---

## Resumen de Aislamiento

| Sprint | Archivos Adelantados | Acción |
| :--- | :---: | :--- |
| **Sprint 2+** (Agenda/Admin UI) | 3 archivos | Documentados, no desactivados (no hay rutas activas) |

> [!IMPORTANT]
> **No se han desactivado rutas en `urls.py`** porque los endpoints de clínicas y usuarios
> ya están protegidos por el middleware RBAC (T018) — un usuario sin rol ADMIN no puede
> acceder a estos recursos. El aislamiento es **lógico** (por permisos), no físico.

---

*Todo el código del repositorio está correctamente etiquetado con su Sprint correspondiente.*
