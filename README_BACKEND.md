# 🛠️ PsicoSystem - Especificaciones del Backend (Sprint 2)

Este documento detalla los aspectos técnicos y endpoints clave para la integración de los módulos del Sprint 2.

## 🔐 Autenticación y Seguridad
- **JWT:** Uso de SimpleJWT para el manejo de sesiones.
- **Roles Corregidos:** Asegurarse de usar los valores exactos: `ADMIN`, `PSICOLOGO`, `PACIENTE`.
- **Bloqueo de Cuenta:** El sistema cuenta con rate-limiting en el login y registro para evitar ataques de fuerza bruta.

## 📅 Módulo de Citas y Logística
- **Validación de Colisiones:** El servidor ahora rechaza citas que tengan menos de 1 hora de diferencia para un mismo psicólogo.
- **Soft-Delete:** Las citas no se eliminan. Se usa el método `DELETE` para marcarlas como `CANCELADA`.
- **Filtros de Agenda:** Puedes filtrar por rango de fechas usando:
  `/api/citas/?fecha_inicio=2023-10-01&fecha_fin=2023-10-31`

## 🤖 Inteligencia Artificial (Google Gemini)
- **Análisis Predictivo:** Endpoint `/api/ia/analizar/<evo_id>/`.
- Procesa las notas de evolución y devuelve un JSON con: resumen, diagnóstico predictivo y sugerencias terapéuticas.

## 💰 Finanzas y Reportes
- **Consulta de Saldo:** `/api/finanzas/saldo/<paciente_id>/`.
- **Recibo PDF:** `/api/finanzas/comprobante/<trans_id>/pdf/`.
- **Reporte Dinámico:** `/api/reportes/personalizado/` (genera texto y audio MP3).
