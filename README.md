PsicoSystem - Plataforma SaaS Multi-tenant para Gestión Psicológica
PsicoSystem es una solución de software bajo el modelo SaaS (Software as a Service) diseñada para la transformación digital de centros psicológicos. La plataforma implementa una arquitectura desacoplada orientada a servicios para garantizar el aislamiento de datos entre instituciones y la escalabilidad del sistema.

Arquitectura del Sistema (T001)
El proyecto se basa en una arquitectura de servicios distribuidos:

Backend: API REST desarrollada en Django 6.0 utilizando Django REST Framework (DRF) para la exposición de endpoints.

Seguridad: Autenticación stateless mediante JSON Web Tokens (JWT) para la interoperabilidad con diferentes clientes.

Frontend Web: Single Page Application (SPA) desarrollada en React.js (en proceso de integración).

Aplicación Móvil: Cliente multiplataforma desarrollado en Flutter (en proceso de integración).

Persistencia: Base de Datos PostgreSQL con esquema de aislamiento lógico (Multi-tenancy) mediante identificadores de Tenant.

Stack Tecnológico (T002)
Lenguaje: Python 3.12+

Framework Web: Django 6.0 & Django REST Framework

Seguridad: PyJWT / SimpleJWT

Motor de Base de Datos: PostgreSQL

Entorno de Ejecución: Entornos virtuales (venv)

Control de Versiones: Git con flujo de trabajo basado en ramas

Estado del Proyecto (Sprint 0 y Sprint 1)
Actualmente, el sistema cuenta con la infraestructura Core validada:

Módulo Organizacional (RF-29): Implementación de la entidad Clinica (Tenant) para el soporte multi-centro y aislamiento de datos.

Módulo de Identidad (RF-01, RF-28): Sistema de usuarios personalizado con roles (Admin, Psicólogo, Paciente) y soporte para JWT.

Capa de Persistencia (T005): Modelos de datos para Clínicas, Usuarios, Pacientes y Citas debidamente migrados.

Capa API (T008, T014): Implementación inicial de Serializers y APIViews para el consumo de datos en formato JSON.

Estructura del Repositorio
psicosystem/: Configuración global del proyecto, configuración de seguridad y middleware.

core/: Lógica de negocio, modelos de datos multi-tenant y serializadores REST.

templates/: Plantillas base de administración (Back-office).

venv/: Entorno virtual de dependencias.

Instalación y Despliegue Local
Clonación del repositorio:
git clone https://github.com/alecaballero17/PsicoSystem_SI2.git

Gestión del entorno virtual:
python -m venv venv
source venv/Scripts/activate (En Windows: venv\Scripts\activate)

Instalación de dependencias críticas:
pip install django djangorestframework djangorestframework-simplejwt psycopg2-binary python-decouple

Configuración de Base de Datos:
Crear una base de datos PostgreSQL denominada db_psicosystem y configurar las variables de entorno para las credenciales en el servidor.

Aplicación de esquema de datos:
python manage.py makemigrations
python manage.py migrate

Ejecución del servicio:
python manage.py runserver

Desarrollo: Alejandro Caballero -Brayan Ramos - Grupo 12 SI2
Institución: Universidad Autónoma Gabriel René Moreno (UAGRM)
