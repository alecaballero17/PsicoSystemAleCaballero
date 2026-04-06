# 🧠 PsicoSystem - Hub de Gestión Clínica para Psicología

![PsicoSystem Architecture](https://img.shields.io/badge/Architecture-Clean%20%7C%20RESTful-2ea44f)
![Status](https://img.shields.io/badge/Status-Beta%20V1.0-blue)
![Django](https://img.shields.io/badge/Backend-Django%20Rest%20Framework-092E20?logo=django)
![React](https://img.shields.io/badge/Web-React.js-61DAFB?logo=react)
![Flutter](https://img.shields.io/badge/Mobile-Flutter-02569B?logo=flutter)

## 📌 Descripción del Proyecto (SI2)
**PsicoSystem** es un sistema ERP en la nube (SaaS Multi-tenant) diseñado para centralizar la gestión de pacientes y agendas de múltiples clínicas psicológicas de forma aislada y segura. Cuenta con una API robusta, un portal administrativo Web, y una App Móvil para acceso de pacientes.

---

## 🏗️ Arquitectura Actual vs. Nueva Propuesta Clean Module

Para la materia de **Sistemas de Información 2 (SI2)**, el sistema evolucionó de un **monolito estándar (MVC)** a una **arquitectura en capas (Clean Module)** enfocada en la segmentación atómica de responsabilidades y la alta escalabilidad.

### 🏛️ 1. Arquitectura Actual (Monolito Base)
Este diseño nos permitió tener un despliegue MVP durante el **Sprint 0** con lógica funcional aglomerada.
```text
psicosystem/         <-- Configuraciones Core, URLs principales y entornos
core/                <-- Módulo Principal (Monolito)
 ┣ migrations/       <-- Tracking de base de datos
 ┣ models.py         <-- Modelos (Clinica, Usuario, Paciente, Cita) todo junto
 ┣ serializers.py    <-- Transformadores de Data Serializada
 ┣ views.py          <-- Toda la lógica de Negocio Web y API
 ┗ permissions.py    <-- Control centralizado de Token/Roles
```
*Problema*: Dificultad para mantener miles de rutas y escalar sin conflictos debido al sobre-acoplamiento de funciones de `Auth`, `Pacientes`, y `Citas` en archivos únicos (`views.py` y `models.py`).

### 🚀 2. Nueva Arquitectura Propuesta (Clean Architecture y Domain-Driven Design)
Divide y vencerás. Cada archivo se ocupa de una única entidad o responsabilidad.
```text
psicosystem/         <-- Configuraciones (Env, Settings, URLs Globales)
core/                <-- Despliegue Segmentado
 ┣ admin/            <-- Registro de panel administrativo dividido
 ┣ models/           <-- Persistencia de Base de Datos
 ┃ ┣ __init__.py
 ┃ ┣ clinica.py      <-- Módulo SaaS
 ┃ ┣ usuario.py      <-- Módulo Seguridad
 ┃ ┣ paciente.py     <-- Módulo Negocio
 ┃ ┗ cita.py         <-- Módulo Transaccional
 ┣ views/            <-- Endpoints y Controladores REST aislados
 ┃ ┣ __init__.py
 ┃ ┣ auth_views.py       <-- Login, Tokens
 ┃ ┣ clinica_views.py    <-- Tenants
 ┃ ┣ paciente_views.py   <-- CRUD Pacientes
 ┃ ┗ dashboard_views.py  <-- Metadatos
 ┣ serializers/      <-- Formateo I/O
 ┃ ┣ __init__.py
 ┃ ┣ auth_serializer.py
 ┃ ┣ clinica_serializer.py
 ┃ ┗ ...
 ┗ security/         <-- Core Defense y RBAC
   ┣ __init__.py
   ┣ permissions.py  <-- Capa Roles (IsAdmin, IsPsicologo)
   ┗ decorators.py
```

### 💻 Frontend (Estructura Definida)
El entorno React.js (**`frontend-web`**) ya funciona bajo este estándar de separación óptima:
*   `api/`: Instancia de Axios con inyección de JWT por interceptores.
*   `services/`: Central de llamadas por entidad (ej. `pacienteService.js`).
*   `pages/`: Vistas estructurales (Login, Dashboard, Formulario Paciente).
*   `components/`: Componentes minificados y atómicos (Navbar, Inputs).
*   `context/`: Manejo de Estado Global de Autenticación.

### 📱 Mobile (Estructura Definida)
Flutter (**`mobile-app`**) diseñado por Features/Layers:
*   `config/`: Inicializadores y Variables de Entorno `.env`.
*   `models/`: Mapeo de Clases fuertemente tipadas de Dart a JSON.
*   `screens/`: Pantallas principales de interfaz al Usuario/Paciente.
*   `services/`: Repositorio (API Calls).
*   `widgets/`: Componentes UI reutilizables (Botones, Textfields).

---

## 🎯 Trazabilidad al Marco Metodológico (Sprints 0 y 1)

### Sprint 0 (Infraestructura):
*   **T001 - T004**: Entornos levantados. Bases de datos ligadas, repositorios sincronizados.
*   **T005 - T006**: MVP Inicial definido.
*   **T007 - T008**: Prototipos y API conectadas (CORS y PostgreSQL funcionando).
*   **T009**: Estándar Swagger (drf-spectacular activo).

### Sprint 1 (Autenticación y Registros Base):
*   **T010 - T011**: Login y Autenticación Criptográfica JWT totalmente operativo (AuthBearer en headers).
*   **T012**: Ingreso Multiplataforma (Móvil).
*   **T013 - T014**: Registro de pacientes interconectados por API segregando la data del usuario según su `Clínica` (SaaS tenant).

### 🏆 Funcionalidades Avances
El equipo implementó antes de lo previsto métricas administrativas reales de Dashboard multi-tenants y un componente robusto `Logout` que introduce a Tokens de tipo *Blacklist* para seguridad incrementada, cubriendo el esquema de **Seguridad de Alta Confiabilidad (RNF-03)** en etapa temprana y creación de `Clinicas`.

### 🚧 Bloqueantes o En Progreso
Restan las vistas (`views/`) e interfaces gráficas para gestionar completamente el flujo final de **Citas**. El modelo persistente existe, pero las peticiones no han sido expuestas gráficamente en todos los ecosistemas requeridos.

---

## 🔐 Pilares Técnicos Implementados
1.  **Aislamiento SaaS Multi-tenant**: Separación física y lógica de información donde los datos de una clínica local o un psicólogo jamás cruzan con los de otra institución gracias a reglas en `models.py` (ForeingKeys obligatorias) y filtros por petición instanciada (`request.user.clinica`).
2.  **Stateless API JWT**: Tokens JSON estandarizados permiten que tanto React como Flutter llamen a Django al mismo tiempo sin colapsar las sesiones en caché.
3.  **Roles (RBAC)**: Se valida severamente la acción del controlador dictando si pertenece al grupo de Administrador global o simple receptor/psicólogo.

### 🛠️ Puesta en Marcha (DevMode)
**Backend:**
```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver
```

**Frontend:**
```bash
cd frontend-web
npm install
npm start
```

**Mobile:**
```bash
cd mobile-app
flutter pub get
flutter run
```
