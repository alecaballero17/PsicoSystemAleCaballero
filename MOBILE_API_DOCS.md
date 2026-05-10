# Documentación de API para Aplicación Móvil (Flutter)

Este documento contiene la información necesaria para conectar la aplicación móvil (Flutter) con el backend (Django). Toda la lógica de autenticación y permisos ha sido adaptada para soportar el flujo de pacientes.

## 🔑 Autenticación
Todos los endpoints están protegidos. Debes obtener un **Token JWT** enviando las credenciales del usuario al endpoint de login general.

*   **Ruta Login:** POST /api/auth/login/
*   **Body:** {"username": "ci_o_usuario", "password": "su_password"}
*   **Uso:** En cada petición descrita abajo, debes enviar el header: Authorization: Bearer <TU_TOKEN>

---

## 1. 💰 Consultar Deuda (Saldo Pendiente)
Este endpoint devuelve el estado financiero actual del paciente. Es útil mostrar esto en la pantalla antes de que el usuario inicie el pago.

*   **Ruta:** GET /api/mobile/paciente/<paciente_id>/saldo/
*   **Permiso:** EsPaciente o IsAuthenticated

**Respuesta Exitosa (HTTP 200 OK):**
`json
{
    "paciente_id": 1,
    "paciente_nombre": "Juan Perez",
    "total_pagado": 100.00,
    "total_deuda_acumulada": 250.00,
    "saldo_pendiente": 150.00
}
`

---

## 2. 💳 Pasarela de Pagos (Simulada)
Cuando el usuario toque "Pagar" en la app móvil, envía los datos de su tarjeta a este endpoint.

*   **Ruta:** POST /api/mobile/paciente/pagar/
*   **Permiso:** EsPaciente o IsAuthenticated

**Body (JSON):**
`json
{
    "paciente_id": 1,
    "monto": 150.00,
    "metodo_pago": "TARJETA",
    "numero_tarjeta": "1234567890123456"
}
`
*(Nota de validación: Para facilitar las pruebas, el servidor solo verificará que la longitud de 
umero_tarjeta sea mayor a 4 caracteres. Si es válida, se registrará el pago y aparecerá automáticamente en el sistema contable web).*

**Respuesta Exitosa (HTTP 201 CREATED):**
`json
{
    "mensaje": "Pago procesado exitosamente por la pasarela virtual.",
    "transaccion_id": 4,
    "comprobante": "MOB-1A2B3C4D",
    "monto_pagado": 150.00
}
`

---

## 3. 🔔 Notificaciones Push (Firebase FCM)
Para que el usuario reciba alertas (ej. confirmación de su pago), el Backend necesita saber el "Token de Dispositivo" que Firebase le asigna al celular.

### Registrar Token FCM
Debes llamar a este endpoint cuando la aplicación inicia y logras capturar el Token de Firebase desde Flutter (irebase_messaging).

*   **Ruta:** POST /api/mobile/notificaciones/registrar-token/
*   **Permiso:** EsPaciente o IsAuthenticated

**Body (JSON):**
`json
{
    "fcm_token": "token_largo_generado_por_firebase_abc123..."
}
`

**Respuesta Exitosa (HTTP 200 OK):**
`json
{
    "mensaje": "Token registrado exitosamente para notificaciones Push.",
    "fcm_token": "token_largo_generado_por_firebase_abc123..."
}
`

### Notas sobre el Envío de la Notificación (Para la Defensa):
*Para garantizar la estabilidad del sistema durante la defensa, el Backend no dispara peticiones HTTP reales a los servidores de Google FCM.* 
En su lugar, cuando ocurre un evento como el pago exitoso, el Backend buscará el cm_token guardado y **simulará** el envío imprimiendo un log completo (título, cuerpo, token destino) en la consola del servidor Django ([FIREBASE PUSH SIMULATOR]). 
Tu única responsabilidad en Flutter es enviarme el token; el backend se encarga del resto.
