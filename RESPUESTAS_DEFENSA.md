# 🛡️ Respuestas Técnicas para Defensa de Grado (PsicoSystem SI2)

A continuación, se exponen las respuestas técnicas estructuradas con terminología de ingeniería de software para defender los mecanismos de seguridad, arquitectura y trazabilidad del sistema.

### 1. Mecanismo de Seguridad Stateless (JWT)
**P: ¿Cómo funciona la autenticación basada en JWT (JSON Web Tokens) en este sistema?**
**R:** El sistema emplea un enfoque HTTP *Stateless* (sin estado). Cuando el usuario ingresa sus credenciales enviando un POST al endpoint de autenticación, el servidor Django valida la identidad contra PostgreSQL. Si es exitosa, no crea ninguna sesión en la memoria del servidor (como lo hacía tradicionalmente con Cookies/SessionID), sino que firma criptográficamente un token (JWT) que contiene el `user_id`, `rol`, y `clinica_id` (Payload). 
El backend confía en este token para peticiones futuras: el frontend (o la app móvil) inyecta el JWT en el *Header Authorization (Bearer)* de cada petición (configurado vía Axios/Interceptors). El backend verifica la firma matemática del token (usando la clave secreta `SECRET_KEY`); si es válido y no ha expirado, procesa la solicitud sin volver a consultar credenciales a la base de datos, garantizando alta disponibilidad y escalabilidad horizontal.

### 2. Arquitectura Multi-tenant (RF-29)
**P: ¿Cómo garantiza el sistema que una clínica no vea los datos de otra?**
**R:** Mediante el principio de **Aislamiento Lógico de Datos (Logical Separation of Data)** en una única base de datos compartida. 
La inyección de contexto asegura el tenant: El ID de la clínica del usuario (`clinica_id`) está embebido o vinculado al objeto de su sesión segura (`request.user.clinica`). En lugar de que el usuario envíe manualmente a qué clínica pertenece (lo cual sería vulnerable a manipulación mediante POST u *Object Reference Vulnerabilities*), el Backend intercepta el Token, decodifica a qué `request.user` pertenece y aplica un QuerySet filtrado de la siguiente forma: `Paciente.objects.filter(clinica=request.user.clinica)`. Este *Tenant Context Injection* asegura a nivel de ORM que cualquier dato que viaje sea explícitamente el de su tenant.

### 3. Control de Acceso Basado en Roles (RBAC)
**P: Detalla qué puede ver y hacer cada perfil según RF-28 y RF-30.**
**R:** El sistema implementa *Role-Based Access Control* (RBAC) validado mediante la inyección de metadatos en el modelo `Usuario`. 
*   **Admin:** Posee privilegios de creación y gestión a nivel organizativo (Gestión de recursos humanos, registro de médicos). Protegido bajo la directiva genérica `IsAdminUser` o permisos customizados backend.
*   **Psicólogo:** Tiene acceso de lectura, escritura y actualización exclusivamente sobre los `Pacientes` y las `Citas` asociadas a su instancia de clínica. 
*   **Paciente:** Nivel base, limitado estrictamente de solo lectura hacia su historia y perfil (Mobile Portal). 
Si un `Paciente` intenta hacer `GET` a `/api/dashboard/` (URL de Admin/Psicólogo), el Middleware de Django REST Framework en la capa de *Permission Classes* (Ej. `permission_classes = [IsPsicologo]`) evalúa la variable `request.user.rol` ANTES de llegar al controlador. Al no cuadrar, emite una excepción HTTP 403 `PermissionDenied` que bloquea instantáneamente el acceso a nivel de API, garantizando **Zero Trust**.

### 4. Diferencia entre SuperAdmin y Admin de Clínica
**P: Explica qué configuración se hace desde el Backoffice/Django Admin y qué gestión hace el Admin de la clínica en la App de React.**
**R:** Existe una segregación de poder técnico frente a poder de negocio:
*   **SuperAdmin (Django Backoffice):** Es el administrador de la **infraestructura y la plataforma**. Gestiona base de datos cruda, migraciones, reseteos catastróficos, habilitación global del sistema SaaS, y creación manual de "Tenant Root Users" (Admins de las clínicas) usando el panel maestro autogenerado por Django. Es equivalente al DevOps/Root.
*   **Admin de Clínica (App React):** Es el administrador **del negocio**. Opera dentro del ecosistema del Frontend, está restringido a la vista de su propia organización (Tenant). Genera personal (psicólogos), recepcionistas y ajusta la configuración interna de esa clínica sin tener impacto en ninguna otra de la BD compartida.

### 5. Trazabilidad de Auditoría (Logs)
**P: Según el requerimiento T023, ¿cómo registra el sistema quién entró y qué cambió en la base de datos PostgreSQL?**
**R:** El sistema emplea la librería estándar de `logging` de Python interconectada a las vistas (Views). Tras cualquier operación mutativa (Ej. Crear clínica, insertar o actualizar pacientes) o fallos de seguridad graves, se dispara un `logger.info()` o `logger.warning()`. Estos logs capturan el evento, el `request.user.username` (quién ejecutó) y el Payload o contexto del cambio. A diferencia de datos en tablas transaccionales, se mantienen en un Stream a consola o archivo `.log`, posibilitando hacer un *tracing* forense (Auditoría Lineal) vitalicio del comportamiento en producción.
