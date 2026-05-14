# 🏥 PsicoSystem SI2 — Plataforma SaaS de Gestión Clínica Asistida por IA

<div align="center">
  <i>PsicoSystem redefine la salud mental digital mediante la integración de analítica avanzada, resiliencia empresarial y diagnósticos predictivos potenciados por Inteligencia Artificial (Google Gemini).</i>
</div>

---

## 🚀 Innovaciones y Características "WOW" (Sprint 2)

### 🤖 IA Resiliente con Degradación Elegante (Graceful Degradation)
Implementación de arquitectura a prueba de fallos para los servicios de Inteligencia Artificial (Google Gemini 1.5 Flash).
- **Diagnóstico Clínico Asistido:** Análisis probabilístico basado en DSM-5-TR a partir de notas clínicas sin longitud mínima requerida.
- **Asistente Ejecutivo por Voz:** Extracción de entidades por NLP y generación de narrativa ejecutiva hablada.
- **Contingencia Automática (Mock Data):** Si la API de Google falla (Error 429/503 por saturación), el sistema detecta la caída y automáticamente inyecta *Mock Data* predefinido, garantizando un 100% de uptime visual durante demostraciones en vivo.

### 🔔 Web Push Notifications Nativas
Integración directa con la API de Notificaciones del Sistema Operativo.
- Alertas en tiempo real para agendamientos de citas, cancelaciones y resultados de diagnósticos IA.
- Gestión inteligente de permisos (Request Permission Flow) adaptada para entornos de producción (Vercel/Render).

### 📅 Motor Logístico de Citas Blindado
Algoritmo estricto para evitar colisiones de agenda y proteger la consistencia de los datos.
- **Prevención de Carrera (Race Conditions):** Bloqueo reactivo de UI para evitar el "doble clic" que genera falsos positivos en colisiones.
- **Filtro Multi-tenant:** Los pacientes solo pueden ser agendados con psicólogos que pertenezcan a su misma clínica.

### 💎 Arquitectura Multi-tenant Hardened (SaaS)
Aislamiento total de datos a nivel de base de datos (Query filtering por `clinica_id`).
- **Seguridad RBAC:** Roles de Administrador (Gestión total) y Psicólogo (Gestión clínica).
- **Onboarding Atómico:** Flujo de registro que vincula automáticamente la clínica con su primer administrador.

---

## 🛡️ Seguridad, Auditoría y Portabilidad

El sistema implementa los estándares de seguridad y trazabilidad más rigurosos, listos para auditoría:

- **Bitácora de Auditoría (RF-30):** Registro inmutable de cada acción crítica (Logins, creación de pacientes, reportes, IA) con timestamp y usuario responsable.
- **Portabilidad y Continuidad de Negocio (Backup/Restore):**
    - **Exportación Manual:** Volcado de toda la base de datos de la clínica en formato JSON portable.
    - **Restauración Inteligente:** Regeneración automática del tenant y sus relaciones de base de datos a partir del JSON.
    - **Botón del Pánico:** Endpoint de destrucción controlada (`DestruccionControladaAPIView`) para purga total operativa y demostración de recuperación de desastres (Disaster Recovery).

---

## 🛠️ Arquitectura de Módulos

| Módulo | Descripción | Estado |
| :--- | :--- | :--- |
| **P1: Identidad y Acceso** | Gestión SaaS, Multi-tenancy y seguridad JWT estricta. | ✅ 100% |
| **P2: Gestión Clínica** | Expediente digital, CRUD de pacientes (incluye borrado lógico). | ✅ 100% |
| **P3: Logística de Citas** | Agenda inteligente, notificaciones Push y validación Anti-Choque. | ✅ 100% |
| **P4: IA y Administración** | Reportes Gemini, Bitácora, Finanzas y Resiliencia Mock Data. | ✅ 100% |

---

## 📊 Módulo de Reportes Financieros
- **Generador de PDF:** Reportes oficiales de pagos y transacciones utilizando `ReportLab`.
- **Comprobantes:** Emisión automática de recibos en PDF con diseño institucional premium para descarga directa por el paciente.

---

## 💻 Stack Tecnológico
- **Backend:** Python 3.12 + Django 6.0 + Django REST Framework.
- **Base de Datos:** PostgreSQL (Producción en Render) / SQLite (Desarrollo).
- **Frontend:** React 19 + Axios (Interceptors) + Vercel Deployment.
- **Integraciones:** Google Generative AI (Gemini Flash SDK) + Web Notification API.

---

## 📦 Instalación Rápida
1. **Backend:** 
   - `pip install -r requirements.txt`
   - Configurar `GEMINI_API_KEY` en `.env`.
   - `python manage.py migrate` && `python manage.py runserver`
2. **Frontend:** 
   - `cd frontend-web`
   - `npm install` && `npm start`

---
<div align="center">
  <i>Desarrollado para la defensa final de Sistemas de Información II</i>
</div>
