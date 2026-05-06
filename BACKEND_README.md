# 🚀 Manual de Integración de Backend - Sprint 2 (PsicoSystem SI2)

Este documento es una guía técnica exhaustiva para el equipo de **Frontend (Web y Móvil)**. Contiene todos los endpoints, estructuras de datos esperadas y detalles de implementación necesarios para conectar las interfaces con el Backend.

## 🔗 Enlaces Base
- **URL BASE DE LA API:** `http://localhost:8000/api/`
- **DOCUMENTACIÓN INTERACTIVA (SWAGGER):** `http://localhost:8000/api/docs/swagger/`

---

## 🔐 1. Seguridad y Autenticación (Módulo P1)
Todas las peticiones (excepto el login y registro) requieren el encabezado de autorización:
```http
Authorization: Bearer <tu_access_token>
```

### Login y Expiración de Claves (SEC-02)
- **Endpoint:** `POST /api/auth/login/`
- **Payload:** `{ "username": "...", "password": "..." }`
- **⚠️ Atención Frontend:** Si en la respuesta JSON recibes `"must_change_password": true`, el sistema ha detectado que la clave tiene más de 90 días. **DEBES bloquear el acceso** al sistema y redirigir al usuario a una pantalla de cambio de clave.

---

## 🏥 2. Gestión Clínica Avanzada (Módulo P2)

### Búsqueda y Filtrado de Pacientes (T027)
- **Endpoint:** `GET /api/pacientes/?search=<texto>`
- **Uso:** El parámetro `search` busca tanto por Nombre como por CI (DNI) de forma simultánea. Ideal para la barra de búsqueda del Dashboard.

### Historia Clínica y Evolución (T026)
- **Expedientes:** `GET /api/historias/<paciente_id>/`
  *Nota: La historia se crea automáticamente al registrar un paciente.*
- **Evoluciones (Notas de Sesión):** `POST /api/evoluciones/`
- **⚠️ Atención Frontend (Multipart):** Si envías archivos adjuntos, debes configurar tu petición como `multipart/form-data`, no como JSON.
  - Campos esperados: `historia` (ID), `notas_sesion` (texto), `archivo_adjunto` (file).

---

## 🤖 3. Inteligencia Artificial (Módulo P4 - IA-01)
Integra el poder de Gemini 1.5 Flash para asistir al psicólogo.

### Análisis Predictivo de Sesión
- **Endpoint:** `POST /api/ia/analizar/<evolucion_id>/`
- **Funcionamiento:** Toma el texto de la `nota_sesion` de una evolución ya guardada, lo envía a Gemini y guarda el resultado en el campo `analisis_ia`.
- **Respuesta esperada:** Un JSON con un resumen emocional, diagnóstico preliminar y sugerencias para la próxima sesión. Ideal para mostrar en una tarjeta visual al lado de las notas del psicólogo.

---

## 📅 4. Logística y Citas (Módulo P3)

### Validación de Colisiones (T030)
- **Endpoint:** `POST /api/citas/`
- **⚠️ Atención Frontend:** Al intentar crear o reprogramar una cita, si el psicólogo ya tiene otra cita en ese horario exacto, el backend devolverá un error HTTP 400. Debes capturar este error y mostrar un Toast o Alerta al usuario diciendo: *"El psicólogo ya tiene una cita en ese horario"*.

### Lista de Espera (T031)
- **Endpoints:** `GET /api/lista-espera/` | `POST /api/lista-espera/`
- **Uso:** Para pacientes que necesitan cita urgente pero no hay cupo. El backend los ordena automáticamente por nivel de `prioridad` (Alta, Media, Baja).

---

## 💰 5. Finanzas y Cobros (Módulo P4 - T058 / T059)

### Lógica de Saldos (T058)
- **Endpoint:** `GET /api/finanzas/saldo/<paciente_id>/`
- **Uso:** Devuelve el cálculo automático de cuánto dinero debe el paciente en función de las sesiones a las que asistió y no pagó.

### Registro de Pagos y Recibos PDF (T059)
- **Pago:** `POST /api/finanzas/transacciones/` (Enviar `tipo_transaccion='PAGO'`).
- **Comprobante PDF:** `GET /api/finanzas/comprobante/<transaccion_id>/pdf/`
- **⚠️ Atención Frontend:** Este endpoint no devuelve JSON, devuelve el archivo binario (`application/pdf`). Debes manejarlo en el frontend forzando una descarga con `Blob` o abriéndolo en una nueva pestaña (`window.open`).

---
*Fin del documento.*
