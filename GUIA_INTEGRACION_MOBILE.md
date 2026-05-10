# 📱 Guía de Integración Mobile - PsicoSystem

## 📌 Flujo de Login
1. Enviar credenciales a /api/auth/login/.
2. Almacenar el ccess token de forma segura.
3. Verificar el campo debe_cambiar_password. Si es 	rue, redirigir a la pantalla de cambio de contraseña obligatoria.

## 📌 Gestión de Citas
- Para agendar: Validar que el paciente_id y psicologo_id existan.
- Para cancelar: Usar el método DELETE sobre la cita específica. La respuesta exitosa confirma que el estado pasó a CANCELADA.

## 📌 Notificaciones Push
- El backend está preparado para integrarse con FCM (Firebase Cloud Messaging). Solo falta registrar el token del dispositivo en el endpoint correspondiente.
