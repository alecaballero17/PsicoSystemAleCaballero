# 🏥 PsicoSystem SI2 — Plataforma SaaS de Gestión Clínica Asistida por IA

PsicoSystem es una solución integral diseñada para modernizar la gestión de centros psicológicos, integrando analítica avanzada y diagnósticos predictivos mediante Inteligencia Artificial (Google Gemini).

---

## 🚀 Innovaciones del Sprint 2 (The "WOW" Factor)

### 🎙️ IA de Reportes por Voz (REQUERIMIENTO VIP)
Implementación de un asistente ejecutivo basado en **Gemini 1.5 Flash**. El administrador puede solicitar resúmenes de datos mediante lenguaje natural.
- **Procesamiento:** Conversión de voz a texto -> Extracción de entidades (Regex/NLP) -> Consulta SQL -> Generación de narrativa ejecutiva.
- **Síntesis:** La IA no solo muestra los datos, sino que genera un resumen narrado por voz.

### 📅 Agenda con Blindaje de Colisiones (CU15/T030)
Motor de validación lógica que impide el agendamiento duplicado para un mismo profesional.
- **Validación RNF-05:** Precisión temporal en milisegundos para evitar traslapes.
- **Estado Dinámico:** Gestión de estados (Pendiente, Asistió, Cancelada) con actualización en tiempo real.

### 💎 Arquitectura Multi-tenant Hardened (SaaS)
Aislamiento total de datos a nivel de base de datos (Query filtering por `clinica_id`).
- **Seguridad RBAC:** Roles de Administrador (Gestión total) y Psicólogo (Gestión clínica).
- **Onboarding Atómico:** Flujo de registro que vincula automáticamente la clínica con su primer administrador.

---

## 🛠️ Arquitectura de Módulos

| Módulo | Descripción | Estado |
| :--- | :--- | :--- |
| **P1: Identidad y Acceso** | Gestión SaaS, Multi-tenancy y seguridad JWT. | ✅ 100% |
| **P2: Gestión Clínica** | Expediente digital, registro de pacientes y notas. | ✅ 100% |
| **P3: Logística de Citas** | Agenda inteligente, validación de horarios y lista de espera. | ✅ 100% |
| **P4: IA y Administración** | Reportes Gemini, Bitácora de Auditoría y Finanzas. | ✅ 100% |

---

## 🛡️ Seguridad y Auditoría (Requerimientos Docente)
El sistema cumple con estándares rigurosos de auditoría:
- **Bitácora de Sucesos:** Registro automático de acciones críticas (Logins, Diagnósticos, Pagos).
- **Validación de Passwords:** Políticas de complejidad y requerimiento de cambio periódico.
- **Persistencia Segura:** Encriptación PBKDF2 para credenciales de acceso.

---

## 🛠️ Stack Tecnológico
- **Backend:** Python 3.12 + Django 6.0 + DRF.
- **Frontend:** React 19 + Axios (Interceptors) + Modern CSS.
- **IA:** Google Generative AI (Gemini Flash SDK).
- **Reportes:** ReportLab (Generación de PDF on-the-fly).

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

*Desarrollado para la defensa final del Sprint 2 — PsicoSystem redefine la salud mental digital.*
