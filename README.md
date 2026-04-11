# 🧠 PsicoSystem - Arquitectura Modular y SaaS Multi-tenant

Bienvenido al repositorio oficial del proyecto **PsicoSystem**, un sistema de gestión clínica psiquiátrica y psicológica estructurado con los más estrictos estándares de ingeniería de software (SI2). 

Este documento ha sido generado para la Defensa Técnica y detalla las decisiones arquitectónicas implementadas para garantizar la **separación de responsabilidades**, **escalabilidad**, y **trazabilidad estricta**.

---

## 🏗 Evolución de la Arquitectura

### 🛑 Estado Anterior (Monolito Acoplado)
Inicialmente, el proyecto contaba con estructuras genéricas que dificultaban la mantenibilidad y promovían el código espagueti:
- **Backend**: Todo centralizado en una capeta general `core/` donde los modelos, vistas, serializers y lógica compartían espacio sin un límite claro.
- **Frontend**: Componentes y vistas aglomerados en `src/` sin distinción entre UI, reglas de negocio o llamadas HTTP.
- **Mobile**: Lógica de red y de UI fuertemente acoplada en un solo conjunto principal.

### ✅ Estado Actual (Modularización Extrema y Domain-Driven)
Para resolver la deuda técnica e implementar un verdadero ecosistema **SaaS Multi-tenant**, la aplicación ha sido reestructurada basándose en principios de **Clean Architecture**:

#### 1. Backend (Django + PostgreSQL)
Dividido por responsabilidad funcional y seguridad:
```text
core/
├── admin/          # Configuración del panel de control de Django
├── models/         # (Data Object Layer) - Entidades separadas: usuario.py, clinica.py...
├── serializers/    # (DTO Layer) - Transformación de datos y validaciones
├── views/          # (Controller Layer) - Endpoints API REST agnósticos al UI
└── security/       # (Security Layer) - RBAC, Permisos y Autenticación JWT Centralizada
```

#### 2. Frontend Web (React)
Diseño Atómico y Separation of Concerns:
```text
src/
├── api/            # Configuración base de Axios (Tokens, Interceptors)
├── components/     # UI Reutilizable (Botones, inputs genéricos)
├── pages/          # Vistas de presentación completas (Dashboard, Login)
├── services/       # Reglas de negocio y fetching (pacienteService.js, etc.)
└── context/        # Estado global e inyección de dependencias (AuthContext.js)
```

#### 3. Mobile App (Flutter)
Estructura MVVM / Modular State:
```text
lib/
├── config/         # Variables de entorno e IPs (api_config.dart)
├── models/         # Serialización JSON (Data classes)
├── screens/        # Vistas y flujos de pantalla
├── services/       # Conexiones API asíncronas
└── widgets/        # Componentes UI reutilizables
```

---

## 🔐 Matriz de Requerimientos y Seguridad

El sistema está alineado con un enfoque **SaaS Multi-tenant**. 
- **RF-01 (Autenticación JWT)**: Control de acceso sin estado (SimpleJWT + Cookies/LocalStorage).
- **RF-28 (RBAC)**: Manejo de jerarquías (`ADMIN`, `PSICOLOGO`, `PACIENTE`).
- **RF-29 (Data Isolation)**: Cada modelo de negocio tiene un `ForeignKey` obligatorio hacia la entidad `Clinica`. Un tenant no puede acceder a los datos de otro.

---

## 🚀 Flujo de Despliegue para Evaluación (SI2)

### Backend
1. Activar entorno virtual: `source venv/bin/activate` (Linux/Mac) o `venv\Scripts\activate` (Windows).
2. Instalar dependencias: `pip install -r requirements.txt`.
3. Iniciar servidor API: `python manage.py runserver`.

### Frontend Web
1. Ir a `frontend-web/`.
2. Instalar módulos: `npm install`.
3. Levantar React: `npm start`.

### Mobile
1. Ir a `mobile-app/`.
2. Habilitar la lectura de `.env` en `pubspec.yaml` e instalar variables: `flutter pub get`.
3. Levantar app: `flutter run`.

---
*Documentación generada y auditada rigurosamente para el aseguramiento de calidad del Ciclo 1 (SI2).*
