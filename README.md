# 🧠 PsicoSystem SI2 - Gestión Clínica Profesional

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.0-green.svg)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)
[![Flutter](https://img.shields.io/badge/Flutter-3.x-cyan.svg)](https://flutter.dev/)

**PsicoSystem** es una plataforma integral de gestión para clínicas psiquiátricas y psicológicas, diseñada bajo una arquitectura **SaaS Multi-tenant**. Este proyecto implementa estándares rigurosos de ingeniería de software (SI2) para garantizar escalabilidad, seguridad stateless (JWT) y una clara separación de responsabilidades.

---

## 🏗️ Arquitectura del Sistema

El ecosistema se divide en tres capas principales que interactúan mediante una API REST protegida:

1.  **Backend (Core API)**: Django + PostgreSQL. Implementa **Clean Architecture** y **RBAC** (Role-Based Access Control).
2.  **Frontend Web (Panel Administrativo)**: React. Enfocado en la gestión de expedientes, reportes y configuración de la clínica.
3.  **Mobile App (Gestión Rápida)**: Flutter. Orientado a psicólogos y pacientes para consultas de citas y seguimiento.

---

## 📋 Requisitos Previos

Asegúrese de tener instaladas las siguientes herramientas en su entorno:

- **Python 3.11+**
- **Node.js 18+** y npm
- **Flutter SDK** (para la app móvil)
- **PostgreSQL 15+**

---

## 🚀 Guía de Instalación Rápida

### 1. Clonar el repositorio
```bash
git clone https://github.com/brayanjoelrv/PsicoSystemSI2.git
cd PsicoSystemSI2
```

### 2. Configuración del Backend (Django)
```bash
# Crear y activar entorno virtual
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# IMPORTANTE: Edite el archivo .env con sus credenciales de Postgres
```

### 3. Configuración de la Base de Datos
Asegúrese de que PostgreSQL esté corriendo y ejecute:
```bash
# Opcional: Resetear DB si es necesario
python reset_db.py

# Aplicar migraciones
python manage.py makemigrations
python manage.py migrate
```

### 4. Configuración del Frontend Web
```bash
cd frontend-web
npm install
```

### 5. Configuración de Mobile App
```bash
cd mobile-app
flutter pub get
```

---

## 💻 Ejecución del Proyecto

### Backend API
Desde la raíz del proyecto:
```bash
python manage.py runserver
```

### Frontend Web
Desde `frontend-web/`:
```bash
npm start
```

### Mobile App
Desde `mobile-app/`:
```bash
flutter run
```

---

## 🔐 Seguridad y Auditoría

- **Autenticación**: Basada en **JWT (SimpleJWT)** con rotación de tokens.
- **Autorización**: Roles estrictos (`ADMIN`, `PSICOLOGO`, `PACIENTE`).
- **Aislamiento de Datos**: Arquitectura Multi-tenant que asegura que una clínica no pueda acceder a datos de otra.
- **Trazabilidad**: Sistema de logs y auditoría integrado en el backend.

---

## 🛠️ Solución de Problemas

- **Error de conexión a DB**: Verifique que los valores en `.env` (DB_PASSWORD) coincidan con su instalación de Postgres.
- **IP del Servidor**: Si prueba la App Móvil en un dispositivo físico, asegúrese de cambiar `SERVER_IP` en el `.env` y en la configuración de Flutter por la IP local de su PC.
- **CORS Errors**: Verifique que `CORS_ALLOWED_ORIGINS` incluya el host de su frontend web.

---

## 🤝 Créditos
Desarrollado y Auditado por **Brayan Joel RamosV**. 
Proyecto para la materia **Sistemas de Información II (SI2) - UAGRM**.

---
*Estatus del Proyecto: **Fusión Arquitectónica Completada y Auditada 100%** conforme a los estándares de Ingeniería de Software II (UAGRM).*
