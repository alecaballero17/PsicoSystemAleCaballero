# 📋 Definition of Done (DoD) — PsicoSystem SI2

**Documento:** [SPRINT 0 - T009] Estándares de Ingeniería  
**Versión:** 1.0  
**Fecha:** 2026-04-11

---

## Propósito

Este documento define los criterios mínimos que una **Tarea (T)**, **Historia de Usuario (HU)** o
**Caso de Uso (CU)** debe cumplir para ser considerado **TERMINADO** en el backlog del proyecto.

---

## Criterios Obligatorios

### 1. Código Fuente
- [ ] El código compila y ejecuta sin errores (`python manage.py check`, `npm start`, `flutter run`).
- [ ] Cumple con las convenciones de nomenclatura:
  - Backend (Python): `snake_case` para variables y funciones, `PascalCase` para clases.
  - Frontend (JavaScript): `camelCase` para variables y funciones, `PascalCase` para componentes React.
  - Mobile (Dart): `camelCase` para variables y funciones, `PascalCase` para clases.
- [ ] No contiene credenciales hardcodeadas (`SECRET_KEY`, `DB_PASSWORD`, tokens).
- [ ] Incluye comentarios de trazabilidad: `# [SPRINT X - T0xx]` o `// [SPRINT X - T0xx]`.

### 2. Seguridad (RNF-03)
- [ ] Los endpoints nuevos requieren autenticación JWT (`IsAuthenticated`).
- [ ] Los endpoints con datos sensibles tienen permisos RBAC (`IsAdmin`, `IsPsicologo`).
- [ ] Los datos de un tenant (clínica) no son accesibles por otro tenant (RF-29).
- [ ] Los inputs del usuario están validados y sanitizados en el Serializer.

### 3. Pruebas (RNF-08)
- [ ] Existen tests unitarios o de integración para la funcionalidad implementada.
- [ ] Todos los tests del módulo pasan: `python manage.py test core`.
- [ ] La cobertura global se mantiene ≥ 70%.

### 4. Documentación
- [ ] Los endpoints nuevos aparecen en la documentación OpenAPI (`/api/docs/swagger/`).
- [ ] Los modelos incluyen `help_text` en campos críticos.
- [ ] Las clases y funciones complejas incluyen docstrings.

### 5. Control de Versiones (T003)
- [ ] El commit sigue la convención: `tipo(alcance): descripción`
  - Tipos válidos: `feat`, `fix`, `chore`, `docs`, `test`, `refactor`.
  - Ejemplo: `feat(auth): implementar logout con blacklist JWT`.
- [ ] El commit se realiza en una rama `feature/*` y se fusiona a `dev` mediante merge.

### 6. Revisión de Pares
- [ ] El código ha sido revisado por al menos un miembro del equipo.
- [ ] Los comentarios de la revisión han sido resueltos.

---

## Criterios Opcionales (Recomendados)
- [ ] La funcionalidad ha sido probada en navegadores modernos (Chrome, Firefox, Edge).
- [ ] La funcionalidad ha sido validada en un dispositivo móvil (Android 11+ / iOS 15+).
- [ ] Se ha verificado que no se introducen regresiones en funcionalidades existentes.
- [ ] El rendimiento de los endpoints no supera los 500ms de tiempo de respuesta.

---

## Flujo de Verificación

```text
Desarrollador → Code Review → Tests Automáticos → Merge a dev → QA Manual → Merge a main
```

---

*Este documento es un artefacto vivo y se actualiza al inicio de cada Sprint.*
