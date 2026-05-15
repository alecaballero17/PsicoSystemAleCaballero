# 🏥 PsicoSystem SI2 — Plataforma SaaS de Gestión Clínica Asistida por IA

<div align="center">
  <img src="https://img.shields.io/badge/Status-Defensa_Final-green?style=for-the-badge" />
  <img src="https://img.shields.io/badge/AI-Gemini_%26_Groq-blueviolet?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Author-Alejandro_Caballero-blue?style=for-the-badge" />
</div>

---

## 🚀 Innovaciones y Arquitectura de Resiliencia (The "WOW" Factor)

### 🎙️ IA de Reportes por Voz (REQUERIMIENTO VIP)
Implementación de un asistente ejecutivo de alto rendimiento para la toma de decisiones.
- **Motor:** **Groq Llama 3.1 (8B)** — Elegido por su latencia ultra-baja (LPUs).
- **Funcionalidad:** Conversión de voz a texto -> Extracción de entidades por NLP -> Consulta dinámica de base de datos -> Narrativa ejecutiva personalizada.
- **Resiliencia:** Si la API de Groq falla, el sistema cuenta con un modo de contingencia local que garantiza la continuidad de la demostración.

### 🧠 Diagnóstico Clínico de 3 Niveles (Tiered AI Architecture)
Un motor de diagnóstico único que combina lo mejor de múltiples nubes para asegurar un 100% de disponibilidad:
1. **Primario (Gemini 1.5 Flash):** Análisis clínico profundo basado en el DSM-5-TR.
2. **Respaldo (Groq Llama 3.3 70B):** Entra en acción automáticamente si Gemini excede su cuota de peticiones.
3. **Contingencia (Mock Data):** Generación de diagnósticos locales si ambos servicios externos no están disponibles.

### 🔔 Notificaciones Push Nativas y Anti-Colisión
- **Web Push API:** Notificaciones del sistema operativo para agendamientos y resultados de IA.
- **Validación Lógica:** Blindaje contra "Doble Clic" y condiciones de carrera (Race Conditions) para evitar citas duplicadas.

---

## 🛠️ Stack Tecnológico
- **Backend:** Python 3.12 + Django 6.0 + DRF (Autenticación JWT estricta).
- **Base de Datos:** PostgreSQL con aislamiento Multi-tenant (Tenancy isolation).
- **Frontend:** React 19 + Axios Interceptors + Modern UX/UI.
- **IA:** Integración Híbrida Gemini (Google) y Groq (Meta Llama 3).
- **Reportes:** ReportLab para la generación dinámica de comprobantes en PDF.

---

## 🛡️ Seguridad y Auditoría (Ready for Audit)
- **Bitácora de Sucesos (RF-30):** Registro inmutable de cada acción crítica realizada en el sistema.
- **Backup & Disaster Recovery:** Sistema de volcado JSON y restauración inteligente con resolución de conflictos.
- **Panic Button:** Módulo de purga operativa controlada para demostración de recuperación de desastres.

---

## 💻 Guía de Ejecución Local (Localhost)

Para levantar el proyecto en tu entorno local durante la defensa o desarrollo, sigue estos pasos abriendo **dos terminales** en tu editor (ej. VS Code):

### 1. Servidor Backend (Django)
Abre una terminal en la carpeta raíz del proyecto (`PsicoSystem_SI2`):
```powershell
# 1. Activar el entorno virtual
.\venv\Scripts\activate

# 2. Iniciar el servidor de desarrollo
python manage.py runserver
```
El backend estará disponible en: `http://127.0.0.1:8000/`

### 2. Servidor Frontend (React)
Abre una **segunda terminal** y navega a la carpeta del frontend web:
```powershell
# 1. Entrar al directorio del frontend
cd frontend-web

# 2. Iniciar la aplicación de React
npm start
```
El frontend se abrirá automáticamente en tu navegador en: `http://localhost:3000/`

---

## 👤 Desarrollado por
<div align="left">
  <img src="https://github.com/alecaballero17.png" width="100px" style="border-radius:50%" />
  <br>
  <strong>Alejandro Caballero</strong><br>
  <i>Ingeniería Informática — UAGRM</i><br>
  <i>Técnico Medio en Programación Web</i><br>
  <a href="https://github.com/alecaballero17">@alecaballero17</a>
</div>

---
<div align="center">
  <i>PsicoSystem SI2 — Redefiniendo la salud mental digital con resiliencia y precisión.</i>
</div>
