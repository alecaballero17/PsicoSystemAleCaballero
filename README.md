# 🧠 PsicoSystem - SaaS Multi-tenant para Centros Psicológicos

**PsicoSystem** es una plataforma integral diseñada bajo el modelo **SaaS (Software as a Service)** para la transformación digital de centros psicológicos. El sistema permite la gestión clínica, administrativa y el análisis de patrones mediante IA, garantizando la seguridad y el aislamiento de datos entre diferentes instituciones.

---

## 🛠️ Stack Tecnológico

* **Backend & Web:** [Django 6.0](https://www.djangoproject.com/) (Python)
* **Base de Datos:** [PostgreSQL](https://www.postgresql.org/) (Arquitectura Multi-tenant)
* **Gestión de Base de Datos:** [pgAdmin 4](https://www.pgadmin.org/)
* **Control de Versiones:** Git & GitHub

---

## 🚀 Estado del Proyecto (Sprint 1)

Actualmente, el proyecto cuenta con la **Infraestructura Base** desplegada:

* **Módulo Organizacional:** Implementación de la entidad `Clinica` (Tenant) para el soporte multi-centro.
* **Módulo de Identidad:** Sistema de usuarios personalizado con roles (Admin, Psicólogo, Paciente).
* **Módulo de Gestión:** Estructura inicial para el registro de historias clínicas y pacientes.
* **Back-office:** Panel administrativo operativo para la gestión de datos maestros.

---

## 📂 Estructura del Proyecto

* `psicosystem/`: Configuración principal del proyecto (Settings, URLs, WSGI).
* `core/`: Aplicación principal que contiene la lógica de negocio y los modelos Multi-tenant.
* `venv/`: Entorno virtual de desarrollo (excluido en .gitignore).

---

## 🔧 Instalación y Configuración Local

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/alecaballero17/PsicoSystem_SI2.git](https://github.com/alecaballero17/PsicoSystem_SI2.git)

2. Crear y activar entorno virtual:
    python -m venv venv
source venv/Scripts/activate  # En Windows

3. Instalar dependencias:
    pip install django djangorestframework psycopg2-binary

4. Configurar Base de Datos:
    Asegurarse de tener una base de datos en PostgreSQL llamada db_psicosystem y configurar las credenciales en settings.py.

5. Ejecutar Migraciones:
    python manage.py migrate

6. Iniciar Servidor:
    python manage.py runserver

Desarrollado por: Alejandro Caballero - Grupo12 SI2