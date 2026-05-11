# 🏥 PsicoSystem SI2 — Plataforma SaaS de Gestión Clínica Asistida por IA

PsicoSystem es una solución integral diseñada para modernizar la gestión de centros psicológicos, integrando analítica avanzada y diagnósticos predictivos mediante Inteligencia Artificial (Google Gemini 2.0).

---

## 🚀 Características Principales

### 💎 Arquitectura Multi-tenant (SaaS)
- **Aislamiento Total:** Cada clínica posee su propio entorno de datos seguro y aislado (RF-29).
- **Onboarding Automático:** Registro atómico de clínicas, planes de suscripción y usuarios administradores.
- **Seguridad RBAC:** Control de acceso basado en roles (Admin, Psicólogo, Paciente).

### 🤖 Módulo de IA Predictiva (Sprint 2)
- **Diagnóstico Asistido:** Integración con **Google Gemini** para el análisis de notas clínicas.
- **Base Ética:** Sugerencias diagnósticas basadas en los estándares **DSM-5-TR** y **CIE-11**.
- **Historial de IA:** Trazabilidad completa de análisis realizados por paciente.

### 📅 Logística y Gestión Clínica
- **Agenda Inteligente:** Control de citas con motor de validación de colisiones de horarios (T030).
- **Expediente Clínico Digital:** Gestión centralizada de pacientes, notas de sesión y adjuntos.
- **Módulo Financiero:** Registro de pagos y generación automática de recibos digitales (CU11/12).

---

## 🛠️ Stack Tecnológico

- **Backend:** Python 3.12 + Django 6.0 + Django REST Framework.
- **Frontend:** React 19 + Axios + React Router v7.
- **Base de Datos:** SQLite (Desarrollo) / PostgreSQL (Producción).
- **IA:** Google Generative AI SDK (Gemini Flash Latest).
- **Seguridad:** JWT (JSON Web Tokens) para autenticación sin estado.

---

## 📦 Instalación y Despliegue

### Requisitos Previos
- Python 3.10+
- Node.js 18+
- Una API Key de Google AI Studio (Gemini).

### Configuración del Backend
1. Clonar el repositorio: `git clone https://github.com/alecaballero17/PsicoSystem_SI2`
2. Crear entorno virtual: `python -m venv venv`
3. Activar entorno: `venv\Scripts\activate`
4. Instalar dependencias: `pip install -r requirements.txt`
5. Configurar `.env` (Ver `.env.example`):
   ```env
   SECRET_KEY='tu_secret_key'
   GEMINI_API_KEY='tu_google_gemini_key'
   ```
6. Migrar base de datos: `python manage.py migrate`
7. Iniciar servidor: `python manage.py runserver`

### Configuración del Frontend
1. Entrar a la carpeta: `cd frontend-web`
2. Instalar paquetes: `npm install`
3. Iniciar aplicación: `npm start`

---

## 🛡️ Auditoría y Seguridad
El sistema incluye un módulo de **Log de Auditoría** que registra todas las acciones críticas (logins, diagnósticos IA, registros de pagos), garantizando la transparencia y el cumplimiento normativo en el manejo de datos sensibles de salud mental.

---
*Desarrollado para la defensa del Sprint 2 de Sistemas de Información II.*
