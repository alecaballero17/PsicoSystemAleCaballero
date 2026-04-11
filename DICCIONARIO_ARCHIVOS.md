# 🗂️ DICCIONARIO TÉCNICO DE ARCHIVOS Y CARPETAS - PSICOSYSTEM
**Propósito:** Este documento ofrece un desglose total de la estructura física del proyecto, detallando arquitectónicamente la función de cada archivo y subcarpeta. Útil para adjuntar como anexo técnico en la Documentación Oficial (PDF).

---

## 1. 🟢 BACKEND (Servidor Django API REST)

La estructura del servidor rompe el monolito clásico y se divide bajo principios de Clean Architecture Orientada a Dominios.

### Directorio: `/core/` (Lógica central del negocio)
*   **📂 `/models/` (Capa de Base de Datos - ORM)**
    *   `clinica.py`: Instancia maestra del sistema Multi-tenant (Almacena Clínicas para aislar datos).
    *   `usuario.py`: Extensión del modelo de seguridad de Django (Manejo de Roles, vinculado obligatoriamente a una Clínica).
    *   `paciente.py`: Entidad que guarda la historia clínica y demografía, custodiada por su Clínica origen.
    *   `cita.py`: Modelo transaccional para la agenda de los pacientes (Sprint 2).
*   **📂 `/serializers/` (Capa DTO - Transformación)**
    *   `usuario_serializer.py` / `clinica_serializer.py` / `paciente_serializer.py` / `cita_serializer.py`: Se encargan de validar que los datos crudos que entran (JSON) sean correctos antes de ir a PostgreSQL, y de convertir los objetos de la DB a JSON limpio para internet.
*   **📂 `/views/` (Capa de Controladores - Endpoints)**
    *   `auth_views.py`: Procesa el intercambio de contraseñas por llaves maestras encriptadas JWT.
    *   `dashboard_views.py`: Retorna métricas generales y cálculos estadísticos de uso rápido de lectura analítica.
    *   `paciente_views.py`: Procesa las altas (POST), bajas y lecturas (GET) de las entidades de pacientes asegurando el filtro Anti-Hacking (isolar el tenant).
    *   `clinica_views.py`: Controlador de tipo "Súper Administrador" para dar de alta nuevos hospitales en el sistema.
*   **📂 `/security/` (Capa Transversal de Defensa)**
    *   `permissions.py`: Reglas Zero-Trust (Ej: `IsPsicologo`, `IsAdmin`). Cortan el paso si un paciente intenta ver URLs restringidas.
    *   `jwt_serializers.py`: Sobrescribe el comportamiento por defecto de la librería SimpleJWT para añadir el `rol` y la `clinica_id` al interior del token encriptado.

### Raíz del Backend
*   `manage.py`: Script principal ejecutor de comandos Django.
*   `requirements.txt`: El "Contrato de Dependencias" (Librerías Python, PostgreSQL adapter).
*   `/psicosystem/urls.py`: El enrutador principal en forma de árbol que conecta todas las `/views/` hacia un enlace web como `/api/pacientes/`.

---

## 2. 🔵 FRONTEND (Cliente Web - React)

La interfaz utiliza *Separation of Concerns*, separando lo que el ojo ve de la lógica HTTP que viaja por internet.

### Directorio: `/frontend-web/src/`
*   **📂 `/api/` (Configuración de Red base)**
    *   `axiosConfig.js`: Interceptor crítico. Agarra el JWT del usuario de forma automática y lo incrusta silenciosamente en las cabeceras HTTP para que el backend reconozca la sesión en cada click sin preguntar pasword repetidamente.
*   **📂 `/services/` (Lógica de Casos de Uso del Cliente)**
    *   `authService.js` / `pacienteService.js` / `clinicaService.js` / `dashboardService.js`: Clases agnósticas a los colores o a la UI. Únicamente se dedican a mandar JSON mediante Axios y atrapar errores.
*   **📂 `/pages/` (Vistas UI Completas Integrales)**
    *   `Login.js`: Renderiza el formulario de bienvenida de seguridad.
    *   `Dashboard.js`: Renderiza el panel analítico y los menús laterales de la clínica del usuario.
    *   `RegistroPaciente.js` / `RegistroClinica.js`: Interfaces "Dumb" que recogen las variables en inputs para enviarlas a los `.services`.
*   **📂 `/context/` (Manejo Global de Estado)**
    *   *(En caso de existir)* `AuthContext.js`: Permite que la "sesión activa" de un Psicólogo, por ejemplo, esté envuelta tipo tela de araña para todas sus sub-pantallas de manera sincronizada, en lugar de pasar estados componentes por componente.
*   **📂 `/tests/` (QA Suite)**
    *   `Integrity.test.js`: Suite de validación con el motor Jest usado para probar lógicas operativas básicas y asertividades del sistema.

### Raíz del Frontend
*   `package.json`: Contiene las dependencias estructurales para usar la arquitectura Web (React 19+, React Router DOM, Axios, Testing Libraries).
*   `App.js` y `index.js`: Entradas obligatorias al flujo virtual DOM.
*   `App.css` y `index.css`: El sistema fundacional cromático del sistema.

---

## 3. 📱 MOBILE APP (Portal de Pacientes - Flutter)

Arquitectura con base en Estado Asíncrono separando pantallas de llamadas HTTP.

### Directorio: `/mobile-app/lib/`
*   **📂 `/config/` (Configuraciones sensibles)**
    *   `api_config.dart`: Archivo "Traductor" maestro del `baseUrl` que lee la IP mediante inyección de Entornos o IPs forzadas hacia el servidor backend en local o nube.
*   **📂 `/services/` (Gestión HTTP móvil)**
    *   `auth_service.dart`: Recibe credenciales de Dart, contacta a Django REST y almacena el JWT localmente dentro del Sandbox del teléfono.
*   **📂 `/screens/` (La presentación de Interfaz de Usuario UI)**
    *   `login_screen.dart`: Visualización material base de entrada en Mobile.
    *   `paciente_dashboard_screen.dart`: Vista exclusiva para presentar historiales personales restringidos bajo el perfil de `Paciente`.
*   `main.dart`: Raíz inyectora de Material App en Android/iOS.

### Raíz del Mobile
*   `pubspec.yaml`: El corazón inyector de paquetes del teléfono (`flutter_dotenv` y `http`) para garantizar las lecturas del ambiente `.env`.
*   `/android/app/src/main/AndroidManifest.xml`: Control de permisos base de Android OS. Modificado explícitamente para permitir la apertura libre del socket interno de red hacia el servidor backend con `android.permission.INTERNET`.
